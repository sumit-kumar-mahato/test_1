import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

from backend.database import get_connection
from backend.safe_utils import safe_float


def load_shg_geo_product_features():
    """
    Build a per-SHG feature table combining:
    - state, district
    - dominant skill (skill_category)
    - capacity & supply
    - district-level demand for that skill
    - latitude/longitude from india_district_demand_large.csv
    """
    conn = get_connection()

    # Base SHG info
    shg_df = pd.read_sql_query(
        "SELECT id AS shg_id, name, village, district, state FROM shg;",
        conn,
    )

    # SHG capacity data (from shg_production)
    prod_df = pd.read_sql_query(
        """
        SELECT shg_id, product_name, monthly_capacity, supply_ready
        FROM shg_production
        """,
        conn,
    )

    # Skills per member → to infer dominant skill per SHG
    skills_df = pd.read_sql_query(
        """
        SELECT m.shg_id, s.skill_category
        FROM member m
        JOIN member_skills s ON m.id = s.member_id
        """,
        conn,
    )

    conn.close()

    if shg_df.empty or prod_df.empty or skills_df.empty:
        return pd.DataFrame()

    # Dominant skill for each SHG
    dom_skill = (
        skills_df.groupby("shg_id")["skill_category"]
        .agg(lambda x: x.value_counts().idxmax())
        .rename("skill_category")
    )

    # Capacity per SHG
    prod_df["monthly_capacity"] = prod_df["monthly_capacity"].apply(safe_float)
    prod_df["supply_ready"] = prod_df["supply_ready"].apply(safe_float)

    cap_agg = prod_df.groupby("shg_id").agg(
        total_capacity=("monthly_capacity", "sum"),
        total_supply_ready=("supply_ready", "sum"),
    )

    # Merge base + skills + capacity
    features = (
        shg_df.set_index("shg_id")
        .join(dom_skill, how="left")
        .join(cap_agg, how="left")
        .reset_index()
    )

    # Load India-wide district demand data
    demand_df = pd.read_csv("india_district_demand_large.csv")

    # Join on (state, district, skill_category)
    features = features.merge(
        demand_df,
        on=["state", "district", "skill_category"],
        how="left",
    )

    # Fill missing demand + coordinates with defaults
    for col in ["monthly_demand", "priority_level", "latitude", "longitude"]:
        if col not in features.columns:
            features[col] = 0.0
        features[col] = features[col].fillna(0.0)

    # Ensure numeric
    features["total_capacity"] = features["total_capacity"].apply(safe_float)
    features["monthly_demand"] = features["monthly_demand"].apply(safe_float)

    # Demand gap = demand - capacity
    features["demand_gap"] = features["monthly_demand"] - features["total_capacity"]
    features["demand_gap"] = features["demand_gap"].fillna(0.0)

    return features


def compute_geo_demand_clusters(n_clusters: int = 6):
    """
    Cluster SHGs by:
    - geography (latitude, longitude)
    - production capacity
    - local demand for their skill
    - demand gap
    """
    feats = load_shg_geo_product_features()
    if feats.empty:
        return feats, pd.DataFrame()

    # Build feature matrix
    cols = ["latitude", "longitude", "total_capacity", "monthly_demand", "demand_gap"]
    X = feats[cols].astype(float).values

    # Simple normalization
    X_mean = X.mean(axis=0)
    X_std = X.std(axis=0)
    X_std[X_std == 0] = 1.0
    X_norm = (X - X_mean) / X_std

    effective_clusters = min(n_clusters, len(feats))
    if effective_clusters < 1:
        effective_clusters = 1

    kmeans = KMeans(
        n_clusters=effective_clusters,
        random_state=42,
        n_init=10,
    )
    labels = kmeans.fit_predict(X_norm)

    feats["cluster_id"] = labels
    feats["cluster_label"] = feats["cluster_id"].astype(int) + 1

    # Build summary per cluster
    rows = []
    for cid in sorted(feats["cluster_label"].unique()):
        sub = feats[feats["cluster_label"] == cid]
        rows.append(
            {
                "cluster_label": int(cid),
                "num_shgs": len(sub),
                "states": ", ".join(sorted(sub["state"].dropna().unique().tolist())),
                "top_skill": sub["skill_category"].value_counts().idxmax()
                if not sub["skill_category"].dropna().empty
                else "Unknown",
                "avg_capacity": sub["total_capacity"].mean(),
                "avg_demand": sub["monthly_demand"].mean(),
                "avg_gap": sub["demand_gap"].mean(),
            }
        )

    summary_df = pd.DataFrame(rows).sort_values("cluster_label")

    return feats, summary_df
