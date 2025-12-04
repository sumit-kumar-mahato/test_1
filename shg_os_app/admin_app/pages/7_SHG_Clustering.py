import streamlit as st
import pandas as pd

from backend.database import init_db
from backend.clustering_engine import compute_shg_clusters
from components.ui_cards import section_header, glass_card

st.set_page_config(
    page_title="SHG Clustering Intelligence",
    page_icon="🧬",
    layout="wide",
)

init_db()

section_header(
    "SHG Clustering Intelligence",
    "🧬",
    "Automatically group SHGs by income, capacity, savings and skills to identify strong and vulnerable clusters."
)

# Compute clusters
with st.spinner("Computing clusters from SHG data..."):
    shg_features, cluster_summary = compute_shg_clusters(n_clusters=6)

if shg_features.empty:
    st.warning("No SHG data available to cluster. Make sure you have imported synthetic data and have SHGs in the database.")
    st.stop()

# ---- Top metrics ----
total_shgs = len(shg_features)
num_clusters = len(cluster_summary)

largest_cluster_size = int(cluster_summary["num_shgs"].max())
largest_cluster_id = int(
    cluster_summary.loc[cluster_summary["num_shgs"].idxmax(), "cluster_label"]
)

col1, col2, col3, col4 = st.columns(4)
glass_card("Total SHGs", str(total_shgs), "From Adani SHG OS dataset", "🏘️")
glass_card("Clusters", str(num_clusters), "AI-derived SHG segments", "🧩")
glass_card("Largest Cluster", f"Cluster {largest_cluster_id}", f"{largest_cluster_size} SHGs", "📊")
glass_card(
    "Avg Capacity (All)",
    f"{shg_features['total_capacity'].mean():.0f} units",
    "Per SHG (monthly)",
    "⚙️",
)

st.markdown("---")

# ---- Cluster summary table ----
section_header("Cluster Overview", "📊", "High-level stats for each SHG cluster")

cluster_summary_display = cluster_summary.copy()
cluster_summary_display["avg_income"] = cluster_summary_display["avg_income"].round(0)
cluster_summary_display["avg_savings"] = cluster_summary_display["avg_savings"].round(0)
cluster_summary_display["avg_capacity"] = cluster_summary_display["avg_capacity"].round(0)
cluster_summary_display["avg_supply_ready"] = cluster_summary_display["avg_supply_ready"].round(0)

st.table(cluster_summary_display.rename(
    columns={
        "cluster_label": "Cluster",
        "num_shgs": "No. of SHGs",
        "avg_income": "Avg Income (₹)",
        "avg_savings": "Avg Savings (₹)",
        "avg_experience": "Avg Experience (yrs)",
        "avg_capacity": "Avg Monthly Capacity",
        "avg_supply_ready": "Avg Supply Ready",
    }
))

st.markdown("---")

# ---- Chart: SHGs per cluster ----
section_header("SHG Count per Cluster", "📈")
count_df = cluster_summary_display[["cluster_label", "num_shgs"]].set_index("cluster_label")
st.bar_chart(count_df)

st.markdown("---")

# ---- Scatter: Income vs Capacity ----
section_header("Income vs Capacity", "🗺️", "Each dot is an SHG, coloured by cluster.")

scatter_df = shg_features[[
    "cluster_label",
    "name",
    "avg_income",
    "total_capacity",
    "avg_savings",
    "dominant_skill",
    "village",
    "district",
    "state",
]].copy()

scatter_df["cluster_label"] = scatter_df["cluster_label"].astype(int)

# Streamlit's native charts don't show colour legends well, so we show table + group-by view
left, right = st.columns([2, 1])

with left:
    st.scatter_chart(
        scatter_df,
        x="avg_income",
        y="total_capacity",
        size=None,
    )
    st.caption("X-axis: Avg Income (₹), Y-axis: Total Monthly Capacity (units)")

with right:
    st.markdown("#### Cluster-wise Skill Snapshot")
    skill_view = (
        scatter_df.groupby("cluster_label")["dominant_skill"]
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index()
        .rename(columns={"cluster_label": "Cluster", "dominant_skill": "Top Skill"})
    )
    st.table(skill_view)

st.markdown("---")

# ---- Detailed table ----
section_header("SHG-level Cluster View", "📄")

with st.expander("View detailed SHG table", expanded=False):
    table_df = scatter_df.rename(
        columns={
            "cluster_label": "Cluster",
            "name": "SHG Name",
            "avg_income": "Avg Income (₹)",
            "total_capacity": "Total Capacity (units)",
            "avg_savings": "Avg Savings (₹)",
            "dominant_skill": "Dominant Skill",
            "village": "Village",
            "district": "District",
            "state": "State",
        }
    )
    st.dataframe(table_df, use_container_width=True)
