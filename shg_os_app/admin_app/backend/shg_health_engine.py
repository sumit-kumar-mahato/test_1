import pandas as pd

from backend.database import get_connection
from backend.clustering_engine import load_shg_feature_matrix
from backend.safe_utils import safe_float


def _load_product_summary():
    """
    Returns per-SHG product diversity and utilisation.
    Handles empty production tables safely.
    """
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            s.shg_id,
            COUNT(DISTINCT s.product_name) AS product_count,
            SUM(s.monthly_capacity) AS total_capacity,
            SUM(s.supply_ready) AS total_supply_ready
        FROM shg_production s
        GROUP BY s.shg_id
        """,
        conn,
    )
    conn.close()

    # If production table empty — return EMPTY DF with required columns
    if df.empty:
        return pd.DataFrame(
            columns=[
                "shg_id",
                "product_count",
                "total_capacity",
                "total_supply_ready",
                "utilisation",
            ]
        )

    # Normal flow
    df["total_capacity"] = df["total_capacity"].apply(safe_float)
    df["total_supply_ready"] = df["total_supply_ready"].apply(safe_float)

    df["utilisation"] = df.apply(
        lambda row: (row["total_supply_ready"] / row["total_capacity"])
        if safe_float(row["total_capacity"]) > 0
        else 0.0,
        axis=1,
    )

    return df


def compute_shg_health():
    """
    Returns:
      - health_df: One row per SHG with health_score & band.
      - band_summary: Count of SHGs in each band.
    """

    # ---- Load core SHG features ----
    features = load_shg_feature_matrix()
    if features.empty:
        return pd.DataFrame(), pd.DataFrame()

    # numeric safety
    for col in ["avg_income", "avg_savings", "total_capacity", "total_supply_ready"]:
        if col in features.columns:
            features[col] = features[col].apply(safe_float)
        else:
            features[col] = 0.0

    # ---- Load product summary ----
    prod_df = _load_product_summary()

    # Merge (safe even if prod_df empty)
    df = features.merge(prod_df, on="shg_id", how="left")

    # Ensure columns exist
    required_cols = [
        "product_count",
        "total_capacity",
        "total_supply_ready",
        "utilisation",
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = 0.0  # default

    df["product_count"] = df["product_count"].fillna(0).astype(int)
    df["total_capacity"] = df["total_capacity"].apply(safe_float)
    df["total_supply_ready"] = df["total_supply_ready"].apply(safe_float)
    df["utilisation"] = df["utilisation"].apply(safe_float)

    # ---- Health scoring ----
    def compute_row_score(row):
        income = safe_float(row["avg_income"])
        savings = safe_float(row["avg_savings"])
        utilisation = safe_float(row["utilisation"])
        product_count = int(row["product_count"])

        # 1) Income strength (0–30)
        income_score = min(income / 12000.0, 1.0) * 30.0

        # 2) Savings cushion (0–20)
        savings_score = min(savings / 8000.0, 1.0) * 20.0

        # 3) Utilisation (0–25)
        utilisation_score = min(max(utilisation, 0.0), 1.0) * 25.0

        # 4) Diversification (0–20)
        if product_count >= 3:
            div_score = 20
        elif product_count == 2:
            div_score = 15
        elif product_count == 1:
            div_score = 10
        else:
            div_score = 5

        # 5) Data completeness (0–5)
        data_score = 5.0 if income > 0 and savings > 0 else 0.0

        total = income_score + savings_score + utilisation_score + div_score + data_score
        return max(0.0, min(total, 100.0))

    df["health_score"] = df.apply(compute_row_score, axis=1)

    def band(score):
        if score >= 80:
            return "Very Strong"
        elif score >= 65:
            return "Stable"
        elif score >= 50:
            return "Emerging"
        else:
            return "At Risk"

    df["health_band"] = df["health_score"].apply(band)

    band_summary = (
        df.groupby("health_band")["shg_id"]
        .count()
        .reset_index()
        .rename(columns={"shg_id": "num_shgs"})
        .sort_values("num_shgs", ascending=False)
    )

    return df, band_summary
