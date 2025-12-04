import streamlit as st
import pandas as pd

from backend.database import init_db
from backend.insights_engine import (
    get_top_products_by_capacity,
    get_underutilized_shgs,
    get_high_potential_low_income_shgs,
    get_state_summary,
)
from components.ui_cards import section_header, glass_card

st.set_page_config(
    page_title="Market & Expansion Insights",
    page_icon="🌍",
    layout="wide",
)

init_db()

section_header(
    "Market & Expansion Insights",
    "🌍",
    "Identify strong products, underutilised SHGs and high-potential groups for market linkage."
)

# ---- Top-level cards ----
state_summary = get_state_summary()
if state_summary.empty:
    st.warning("No SHG data available. Make sure synthetic data is imported.")
    st.stop()

total_shgs = int(state_summary["num_shgs"].sum())
num_states = state_summary["state"].nunique()
total_capacity = state_summary["total_capacity"].sum()
avg_income_overall = state_summary["avg_income"].mean()

c1, c2, c3, c4 = st.columns(4)
glass_card("Total SHGs", f"{total_shgs}", "Across all states", "🏘️")
glass_card("States Covered", f"{num_states}", "Presence footprint", "🗺️")
glass_card("Total Monthly Capacity", f"{total_capacity:.0f} units", "Sum across SHGs", "⚙️")
glass_card("Avg SHG Income", f"₹{avg_income_overall:,.0f}", "Approximate per group", "💰")

st.markdown("---")

# ---- Section: Top Product Opportunities ----
section_header("Top Products by Capacity", "📦", "Where we have the strongest production muscle.")

top_products = get_top_products_by_capacity(limit=10)
if top_products.empty:
    st.info("No product data available.")
else:
    top_products_display = top_products.copy()
    top_products_display["total_capacity"] = top_products_display["total_capacity"].round(0)
    top_products_display["total_supply_ready"] = top_products_display["total_supply_ready"].round(0)

    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.table(top_products_display.rename(
            columns={
                "product_name": "Product",
                "total_capacity": "Total Capacity (units / month)",
                "total_supply_ready": "Total Supply Ready",
                "num_shgs": "No. of SHGs",
                "states": "No. of States",
            }
        ))

    with c_right:
        chart_df = top_products_display[["product_name", "total_capacity"]].set_index("product_name")
        st.bar_chart(chart_df)
        st.caption("Products with the highest production capacity across SHGs.")

st.markdown("---")

# ---- Section: Underutilised SHGs ----
section_header("Underutilised SHGs", "🧯", "High capacity but low utilisation → need market linkage.")

under_df = get_underutilized_shgs(util_threshold=0.5, min_capacity=150.0)
if under_df.empty:
    st.info("No underutilised SHGs found with the current thresholds.")
else:
    under_df_display = under_df.copy()
    under_df_display["monthly_capacity"] = under_df_display["monthly_capacity"].round(0)
    under_df_display["supply_ready"] = under_df_display["supply_ready"].round(0)
    under_df_display["utilization"] = (under_df_display["utilization"] * 100).round(1)

    st.caption("These SHGs have capacity but are not using it fully. They are prime candidates for demand aggregation and marketing support.")
    st.dataframe(
        under_df_display.rename(
            columns={
                "shg_name": "SHG Name",
                "district": "District",
                "state": "State",
                "product_name": "Product",
                "monthly_capacity": "Capacity (units)",
                "supply_ready": "Supply Ready (units)",
                "utilization": "Utilisation (%)",
            }
        ),
        use_container_width=True,
    )

st.markdown("---")

# ---- Section: High Potential, Low Income ----
section_header(
    "High-Potential but Low-Income SHGs",
    "🚀",
    "Groups with strong capacity but low income → best targets for market expansion."
)

high_pot = get_high_potential_low_income_shgs(
    income_threshold=7000.0,
    capacity_threshold=300.0,
)

if high_pot.empty:
    st.info("No high-potential low-income SHGs found with current filters.")
else:
    hp_display = high_pot[[
        "name",
        "state",
        "dominant_skill",
        "avg_income",
        "avg_savings",
        "total_capacity",
        "total_supply_ready",
    ]].copy()

    hp_display["avg_income"] = hp_display["avg_income"].round(0)
    hp_display["avg_savings"] = hp_display["avg_savings"].round(0)
    hp_display["total_capacity"] = hp_display["total_capacity"].round(0)
    hp_display["total_supply_ready"] = hp_display["total_supply_ready"].round(0)

    st.dataframe(
        hp_display.rename(
            columns={
                "name": "SHG Name",
                "state": "State",
                "dominant_skill": "Dominant Skill",
                "avg_income": "Avg Income (₹)",
                "avg_savings": "Avg Savings (₹)",
                "total_capacity": "Total Capacity (units)",
                "total_supply_ready": "Supply Ready (units)",
            }
        ),
        use_container_width=True,
    )

    st.caption(
        "These SHGs are your **top candidates** for targeted marketing support, "
        "buyer linkages and cross-district deployment."
    )
