import pandas as pd
from backend.database import get_connection
from backend.safe_utils import safe_float
from backend.clustering_engine import load_shg_feature_matrix


def get_top_products_by_capacity(limit: int = 10):
    """
    Returns top products across all SHGs by total monthly capacity.
    """
    conn = get_connection()

    prod_df = pd.read_sql_query(
        """
        SELECT s.shg_id, s.product_name, s.monthly_capacity, s.supply_ready,
               g.name AS shg_name, g.state
        FROM shg_production s
        JOIN shg g ON s.shg_id = g.id
        """,
        conn,
    )
    conn.close()

    if prod_df.empty:
        return pd.DataFrame()

    prod_df["monthly_capacity"] = prod_df["monthly_capacity"].apply(safe_float)
    prod_df["supply_ready"] = prod_df["supply_ready"].apply(safe_float)

    agg = (
        prod_df.groupby("product_name")
        .agg(
            total_capacity=("monthly_capacity", "sum"),
            total_supply_ready=("supply_ready", "sum"),
            num_shgs=("shg_id", "nunique"),
            states=("state", "nunique"),
        )
        .reset_index()
        .sort_values("total_capacity", ascending=False)
        .head(limit)
    )

    return agg


def get_underutilized_shgs(util_threshold: float = 0.5, min_capacity: float = 100.0):
    """
    SHGs where supply_ready / capacity < util_threshold.
    """
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT s.shg_id, g.name AS shg_name, g.district, g.state,
               s.product_name, s.monthly_capacity, s.supply_ready
        FROM shg_production s
        JOIN shg g ON s.shg_id = g.id
        """,
        conn,
    )
    conn.close()

    if df.empty:
        return pd.DataFrame()

    df["monthly_capacity"] = df["monthly_capacity"].apply(safe_float)
    df["supply_ready"] = df["supply_ready"].apply(safe_float)

    df = df[df["monthly_capacity"] > 0]
    df["utilization"] = df["supply_ready"] / df["monthly_capacity"]

    under = df[(df["utilization"] < util_threshold) & (df["monthly_capacity"] >= min_capacity)]
    under = under.sort_values("utilization")

    return under


def get_high_potential_low_income_shgs(
    income_threshold: float = 7000.0,
    capacity_threshold: float = 300.0,
):
    """
    SHGs with high capacity but low avg income.
    These are your 'market linkage opportunity' SHGs.
    """
    features = load_shg_feature_matrix()
    if features.empty:
        return pd.DataFrame()

    df = features.copy()
    df["avg_income"] = df["avg_income"].apply(safe_float)
    df["total_capacity"] = df["total_capacity"].apply(safe_float)

    mask = (df["avg_income"] < income_threshold) & (df["total_capacity"] >= capacity_threshold)
    df = df[mask].sort_values(["total_capacity", "avg_income"], ascending=[False, True])

    return df


def get_state_summary():
    """
    State-wise SHG summary: count, avg income, total capacity.
    """
    features = load_shg_feature_matrix()
    if features.empty:
        return pd.DataFrame()

    df = features.copy()
    df["avg_income"] = df["avg_income"].apply(safe_float)
    df["total_capacity"] = df["total_capacity"].apply(safe_float)

    agg = (
        df.groupby("state")
        .agg(
            num_shgs=("shg_id", "nunique"),
            avg_income=("avg_income", "mean"),
            total_capacity=("total_capacity", "sum"),
        )
        .reset_index()
        .sort_values("num_shgs", ascending=False)
    )

    return agg
