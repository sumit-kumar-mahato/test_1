import streamlit as st
import pandas as pd

from backend.database import init_db
from backend.shg_health_engine import compute_shg_health
from components.ui_cards import section_header, glass_card

st.set_page_config(
    page_title="SHG Health & Risk Index",
    page_icon="🚦",
    layout="wide",
)

init_db()

section_header(
    "SHG Health & Risk Index",
    "🚦",
    "Composite view of each SHG's financial strength, utilisation and diversification."
)

with st.spinner("Computing SHG health scores..."):
    health_df, band_summary = compute_shg_health()

if health_df.empty:
    st.warning("No SHG data found. Make sure synthetic data is imported.")
    st.stop()

total_shgs = len(health_df)
avg_health = health_df["health_score"].mean()

very_strong = (health_df["health_band"] == "Very Strong").sum()
stable = (health_df["health_band"] == "Stable").sum()
emerging = (health_df["health_band"] == "Emerging").sum()
at_risk = (health_df["health_band"] == "At Risk").sum()

c1, c2, c3, c4 = st.columns(4)
glass_card("Total SHGs", str(total_shgs), "Scored in this index", "🏘️")
glass_card("Avg Health Score", f"{avg_health:.1f} / 100", "Overall system health", "📊")
glass_card("Strong & Stable", f"{very_strong + stable}", "High-performing groups", "🟢")
glass_card("At Risk", f"{at_risk}", "Need support / training", "🔴")

st.markdown("---")

# ---- Band distribution ----
section_header("Health Band Distribution", "📈")

band_display = band_summary.copy()
band_display = band_display.set_index("health_band")
st.bar_chart(band_display)

st.caption("Number of SHGs in each health category.")

st.markdown("---")

# ---- Filter & table ----
section_header("SHG-level Health Details", "📋")

col_filter1, col_filter2 = st.columns(2)
band_filter = col_filter1.multiselect(
    "Filter by Health Band",
    options=["Very Strong", "Stable", "Emerging", "At Risk"],
    default=["Very Strong", "Stable", "Emerging", "At Risk"],
)
state_filter = col_filter2.text_input("Filter by State (optional)")

df = health_df.copy()
if band_filter:
    df = df[df["health_band"].isin(band_filter)]
if state_filter.strip():
    df = df[df["state"].str.lower() == state_filter.strip().lower()]

df_display = df[[
    "name",
    "state",
    "district",
    "dominant_skill",
    "health_score",
    "health_band",
    "avg_income",
    "avg_savings",
    "total_capacity",
    "total_supply_ready",
    "product_count",
]].copy()

df_display["health_score"] = df_display["health_score"].round(1)
df_display["avg_income"] = df_display["avg_income"].round(0)
df_display["avg_savings"] = df_display["avg_savings"].round(0)
df_display["total_capacity"] = df_display["total_capacity"].round(0)
df_display["total_supply_ready"] = df_display["total_supply_ready"].round(0)

df_display = df_display.rename(
    columns={
        "name": "SHG Name",
        "state": "State",
        "district": "District",
        "dominant_skill": "Dominant Skill",
        "health_score": "Health Score",
        "health_band": "Health Band",
        "avg_income": "Avg Income (₹)",
        "avg_savings": "Avg Savings (₹)",
        "total_capacity": "Capacity (units)",
        "total_supply_ready": "Supply Ready (units)",
        "product_count": "Product Count",
    }
)

st.dataframe(df_display, use_container_width=True)

st.caption(
    "Use this table to identify SHGs ready for scaling (Very Strong / Stable) "
    "and those needing financial literacy, market linkage or capacity-building (At Risk / Emerging)."
)
