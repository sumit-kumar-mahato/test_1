import pandas as pd
from backend.safe_utils import safe_float, safe_int
from backend.database import get_connection


def load_shg_supply_data():
    """Loads SHG-level data required for deployment matching."""
    conn = get_connection()

    # SHG base info
    shg_df = pd.read_sql_query(
        "SELECT id AS shg_id, name, village, district, state FROM shg;",
        conn,
    )

    # SHG product capability
    product_df = pd.read_sql_query(
        """
        SELECT shg_id, product_name, monthly_capacity, supply_ready
        FROM shg_production
        """,
        conn,
    )

    # Financials per SHG (avg of members)
    fin_df = pd.read_sql_query(
        """
        SELECT m.shg_id, f.monthly_income, f.savings
        FROM member m
        JOIN member_financials f ON m.id = f.member_id
        """,
        conn,
    )

    conn.close()

    # Aggregate financials
    fin_agg = fin_df.groupby("shg_id").agg(
        avg_income=("monthly_income", "mean"),
        avg_savings=("savings", "mean"),
    )

    # Aggregate products + capacity
    cap_agg = product_df.groupby(["shg_id", "product_name"]).agg(
        total_capacity=("monthly_capacity", "sum"),
        total_supply_ready=("supply_ready", "sum"),
    ).reset_index()

    # Merge SHG base + financial summary
    shg_info = shg_df.merge(fin_agg, on="shg_id", how="left")

    return shg_info, cap_agg


def compute_match_score(product_required, qty_required, shg_row):
    """Calculate a 0–100 match score."""
    score = 0

    # 1. Skill/Product match (40 points)
    if shg_row["product_name"].lower() == product_required.lower():
        score += 40

    # 2. Supply readiness (25 points)
    supply_ready = safe_float(shg_row["total_supply_ready"])
    if supply_ready >= qty_required:
        score += 25
    else:
        score += (supply_ready / qty_required) * 25

    # 3. Capacity (20 points)
    cap = safe_float(shg_row["total_capacity"])
    if cap >= qty_required:
        score += 20
    else:
        score += (cap / qty_required) * 20

    # 4. Income stability (10 points)
    income = safe_float(shg_row["avg_income"])
    if income > 12000:
        score += 10
    elif income > 8000:
        score += 7
    elif income > 5000:
        score += 4
    else:
        score += 2

    # 5. Location match (5 points)
    # Boost if district/state matches
    if shg_row["district_match"] == 1:
        score += 5
    elif shg_row["state_match"] == 1:
        score += 3

    return round(score, 2)


def match_shgs_to_demand(location, district, state, product_required, qty_required):
    """Return the top SHG matches for the demand."""

    shg_info, cap_info = load_shg_supply_data()

    # Merge financial + product + capacity info
    df = shg_info.merge(cap_info, on="shg_id", how="left")

    # Fill missing
    df["total_capacity"] = df["total_capacity"].apply(safe_float)
    df["total_supply_ready"] = df["total_supply_ready"].apply(safe_float)
    df["avg_income"] = df["avg_income"].apply(safe_float)

    # Compute location match flags
    df["district_match"] = (df["district"].str.lower() == district.lower()).astype(int)
    df["state_match"] = (df["state"].str.lower() == state.lower()).astype(int)

    # Filter only SHGs who produce this product
    df = df[df["product_name"].str.lower() == product_required.lower()]

    if df.empty:
        return pd.DataFrame(), "No SHG produces this item."

    # Compute scores
    df["match_score"] = df.apply(
        lambda row: compute_match_score(product_required, qty_required, row), axis=1
    )

    # Sort by best match
    df = df.sort_values("match_score", ascending=False)

    return df, None
