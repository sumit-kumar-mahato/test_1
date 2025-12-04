import pandas as pd
from itertools import combinations

from backend.database import get_connection
from backend.safe_utils import safe_float


def load_product_supply_table():
    """
    Aggregate SHG-level product capacity:
    One row per (shg, product).
    """
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            s.shg_id,
            g.name AS shg_name,
            g.village,
            g.district,
            g.state,
            s.product_name,
            SUM(s.monthly_capacity) AS monthly_capacity,
            SUM(s.supply_ready) AS supply_ready
        FROM shg_production s
        JOIN shg g ON s.shg_id = g.id
        GROUP BY
            s.shg_id, g.name, g.village, g.district, g.state, s.product_name
        """,
        conn,
    )
    conn.close()

    if df.empty:
        return df

    df["monthly_capacity"] = df["monthly_capacity"].apply(safe_float)
    df["supply_ready"] = df["supply_ready"].apply(safe_float)

    return df


def get_available_products():
    """
    Return sorted list of unique product names.
    """
    df = load_product_supply_table()
    if df.empty:
        return []
    products = sorted(df["product_name"].dropna().unique().tolist())
    return products


def score_team(combo_rows, qty_required: float):
    """
    Simple scoring logic for a team of SHGs:
    - Coverage of required quantity (using supply_ready)
    - Total capacity
    - Smaller teams get a slight bonus
    """
    total_supply_ready = sum(safe_float(r["supply_ready"]) for r in combo_rows)
    total_capacity = sum(safe_float(r["monthly_capacity"]) for r in combo_rows)
    team_size = len(combo_rows)

    if qty_required <= 0:
        qty_required = 1.0

    # 1) Fulfilment based on supply_ready (0–60 points)
    fulfil_ratio = total_supply_ready / qty_required
    fulfil_score = min(fulfil_ratio, 1.5) / 1.5 * 60.0

    # 2) Capacity backup (0–25 points)
    cap_ratio = total_capacity / qty_required
    cap_score = min(cap_ratio, 2.0) / 2.0 * 25.0

    # 3) Team size bonus (0–15 points) -- fewer SHGs, higher score
    max_team_size = 4
    size_score = ((max_team_size - (team_size - 1)) / max_team_size) * 15.0

    total_score = fulfil_score + cap_score + size_score

    return round(total_score, 2), total_supply_ready, total_capacity


def suggest_collaboration_teams(
    product_required: str,
    qty_required: float,
    state_filter: str = "",
    district_filter: str = "",
    max_team_size: int = 4,
    top_k: int = 5,
):
    """
    Suggest multi-SHG teams to fulfil a bulk order.
    Returns:
      - teams: list of dicts
      - base_df: SHG-product table filtered to that product/region
      - message: error or None
    """
    df = load_product_supply_table()
    if df.empty:
        return [], df, "No capacity data available in database."

    # Filter by product (case-insensitive)
    df = df[df["product_name"].str.lower() == product_required.lower()]
    if df.empty:
        return [], df, f"No SHG produces product '{product_required}'."

    # Optional location filters
    if state_filter.strip():
        df = df[df["state"].str.lower() == state_filter.strip().lower()]
    if district_filter.strip():
        df = df[df["district"].str.lower() == district_filter.strip().lower()]

    if df.empty:
        return [], df, "No SHGs match the given region for this product."

    # Convert to records for combination search
    candidates = df.to_dict("records")

    # Limit team size
    max_team_size = max(1, min(max_team_size, 4))
    max_team_size = min(max_team_size, len(candidates))

    teams = []

    # Generate teams of size 1..max_team_size
    for size in range(1, max_team_size + 1):
        for combo in combinations(candidates, size):
            score, total_supply_ready, total_capacity = score_team(combo, qty_required)
            team_dict = {
                "team_size": size,
                "shg_ids": [r["shg_id"] for r in combo],
                "shg_names": [r["shg_name"] for r in combo],
                "districts": [r["district"] for r in combo],
                "states": [r["state"] for r in combo],
                "product_name": combo[0]["product_name"],
                "total_supply_ready": round(total_supply_ready, 1),
                "total_capacity": round(total_capacity, 1),
                "score": score,
            }
            teams.append(team_dict)

    if not teams:
        return [], df, "Could not form any teams."

    # Sort by score (desc), then by team_size (asc)
    teams_sorted = sorted(teams, key=lambda x: (-x["score"], x["team_size"]))

    # Keep top_k
    teams_sorted = teams_sorted[:top_k]

    # Add rank
    for i, t in enumerate(teams_sorted, start=1):
        t["team_rank"] = i

    return teams_sorted, df, None
