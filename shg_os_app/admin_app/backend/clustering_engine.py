import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from backend.safe_utils import safe_float

from .database import get_connection


def load_shg_feature_matrix():
    """
    Build a feature table per SHG:
    - dominant skill
    - avg member income
    - avg savings
    - avg years of experience
    - total monthly capacity
    - total supply ready
    """
    conn = get_connection()

    # ---- Base SHG info ----
    shg_df = pd.read_sql_query(
        "SELECT id AS shg_id, name, village, district, state FROM shg;",
        conn,
    )

    if shg_df.empty:
        conn.close()
        return pd.DataFrame()

    # ---- Skills per SHG ----
    skills_df = pd.read_sql_query(
        """
        SELECT m.shg_id, s.skill_category, s.years_experience
        FROM member m
        JOIN member_skills s ON m.id = s.member_id
        """,
        conn,
    )

    # ---- Financials per SHG ----
    fin_df = pd.read_sql_query(
        """
        SELECT m.shg_id,
               f.monthly_income,
               f.monthly_expense,
               f.savings
        FROM member m
        JOIN member_financials f ON m.id = f.member_id
        """,
        conn,
    )

    # ---- Capacity per SHG ----
    cap_df = pd.read_sql_query(
        """
        SELECT shg_id, monthly_capacity, supply_ready
        FROM shg_production
        """,
        conn,
    )

    conn.close()

    # Aggregate: dominant skill, avg experience
    if not skills_df.empty:
        # Dominant skill
        dom_skill = (
            skills_df.groupby("shg_id")["skill_category"]
            .agg(lambda x: x.value_counts().idxmax())
            .rename("dominant_skill")
        )
        avg_exp = (
            skills_df.groupby("shg_id")["years_experience"]
            .mean()
            .rename("avg_experience")
        )
    else:
        dom_skill = pd.Series(dtype=str, name="dominant_skill")
        avg_exp = pd.Series(dtype=float, name="avg_experience")

    # Aggregate financials
    if not fin_df.empty:
        fin_agg = fin_df.groupby("shg_id").agg(
            avg_income=("monthly_income", "mean"),
            avg_expense=("monthly_expense", "mean"),
            avg_savings=("savings", "mean"),
        )
    else:
        fin_agg = pd.DataFrame(columns=["avg_income", "avg_expense", "avg_savings"])

    # Aggregate capacity
    if not cap_df.empty:
        cap_agg = cap_df.groupby("shg_id").agg(
            total_capacity=("monthly_capacity", "sum"),
            total_supply_ready=("supply_ready", "sum"),
        )
    else:
        cap_agg = pd.DataFrame(columns=["total_capacity", "total_supply_ready"])

    # Merge all
    features = (
        shg_df.set_index("shg_id")
        .join(dom_skill, how="left")
        .join(avg_exp, how="left")
        .join(fin_agg, how="left")
        .join(cap_agg, how="left")
        .reset_index()
    )

    # Fill missing numeric values with 0
    num_cols = [
        "avg_experience",
        "avg_income",
        "avg_expense",
        "avg_savings",
        "total_capacity",
        "total_supply_ready",
    ]
    for c in num_cols:
        if c in features.columns:
            features[c] = features[c].fillna(0.0)

    # Fill dominant skill if missing
    if "dominant_skill" in features.columns:
        features["dominant_skill"] = features["dominant_skill"].fillna("Unknown")
    else:
        features["dominant_skill"] = "Unknown"

    return features


def compute_shg_clusters(n_clusters: int = 6):
    """
    Returns:
      - shg_features_with_cluster: DataFrame with cluster_id
      - cluster_summary: DataFrame with stats per cluster
    """
    features = load_shg_feature_matrix()
    if features.empty:
        return features, pd.DataFrame()

    # numeric feature matrix
    numeric_cols = [
        "avg_income",
        "avg_savings",
        "avg_experience",
        "total_capacity",
        "total_supply_ready",
    ]

    X = features[numeric_cols].values

    # If SHGs < clusters, reduce clusters
    effective_clusters = min(n_clusters, len(features))
    if effective_clusters < 1:
        effective_clusters = 1

    kmeans = KMeans(
        n_clusters=effective_clusters,
        random_state=42,
        n_init=10,
    )
    cluster_labels = kmeans.fit_predict(X)

    features["cluster_id"] = cluster_labels

    # Make cluster labels start from 1 for display
    features["cluster_label"] = features["cluster_id"].astype(int) + 1

    # Build summary
    summary_rows = []
    for cid in sorted(features["cluster_label"].unique()):
        sub = features[features["cluster_label"] == cid]
        summary_rows.append(
            {
                "cluster_label": int(cid),
                "num_shgs": len(sub),
                "avg_income": sub["avg_income"].mean(),
                "avg_savings": sub["avg_savings"].mean(),
                "avg_experience": sub["avg_experience"].mean(),
                "avg_capacity": sub["total_capacity"].mean(),
                "avg_supply_ready": sub["total_supply_ready"].mean(),
            }
        )

    cluster_summary = pd.DataFrame(summary_rows).sort_values("cluster_label")

    return features, cluster_summary
