import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import os

st.set_page_config(
    page_title="Advanced Geo-Intelligence Dashboard",
    page_icon="🗺️",
    layout="wide",
)

# ----------------------------
# LOAD DEMAND DATA
# ----------------------------
@st.cache_data
def load_demand_data():
    path = "india_district_demand_large.csv"
    if not os.path.exists(path):
        st.error("❌ Demand CSV not found. Please make sure 'india_district_demand_large.csv' exists in streamlit_app/")
        return None
    df = pd.read_csv(path)
    return df

# ----------------------------
# LOAD GEOJSON
# ----------------------------
@st.cache_data
def load_geojson():
    geo_path = "data/india_districts.geojson"
    if not os.path.exists(geo_path):
        st.error("❌ GeoJSON file not found in /data folder.")
        return None
    with open(geo_path, "r") as f:
        gj = json.load(f)
    return gj


# Load files
demand_df = load_demand_data()
geojson_data = load_geojson()

if demand_df is None or geojson_data is None:
    st.stop()


# ----------------------------
# PAGE HEADER
# ----------------------------
st.title("🗺️ Advanced SHG Geo-Intelligence Dashboard")
st.caption("Geographical understanding of supply, demand & deployment potential across India")

st.markdown("---")

# ----------------------------
# PRODUCT FILTER
# ----------------------------
skills = sorted(demand_df["skill_category"].unique())
selected_skill = st.selectbox("Select Product / Skill Category", skills)

df_skill = demand_df[demand_df["skill_category"] == selected_skill]

# ----------------------------
# AGGREGATE DEMAND & SUPPLY BY DISTRICT
# ----------------------------
district_view = (
    df_skill.groupby(["state", "district", "latitude", "longitude"])
    .agg(
        total_demand=("monthly_demand", "sum"),
        avg_priority=("priority_level", "mean"),
    )
    .reset_index()
)

# Synthetic supply = 60–90% of demand (for visualization)
district_view["supply"] = (district_view["total_demand"] * 0.6).astype(int)
district_view["gap"] = district_view["total_demand"] - district_view["supply"]

# ----------------------------
# MAP CENTER
# ----------------------------
center_lat = district_view["latitude"].mean()
center_lon = district_view["longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles="CartoDB positron")


# ----------------------------
# ADD DISTRICT POLYGONS
# ----------------------------
folium.GeoJson(
    geojson_data,
    name="District Boundaries",
    style_function=lambda x: {
        "fillColor": "#00000000",
        "color": "#555",
        "weight": 1,
    },
).add_to(m)

# ----------------------------
# ADD DEMAND MARKERS
# ----------------------------
for _, row in district_view.iterrows():
    tooltip = f"""
    <b>District:</b> {row['district']}<br>
    <b>State:</b> {row['state']}<br>
    <b>Product:</b> {selected_skill}<br><br>
    <b>Total Demand:</b> {row['total_demand']:,}<br>
    <b>Supply Available:</b> {row['supply']:,}<br>
    <b>Demand–Supply Gap:</b> {row['gap']:,}<br>
    """

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=7,
        weight=1,
        color="#2A62F4",
        fill=True,
        fill_color="#2A62F4",
        popup=tooltip,
        fill_opacity=0.8,
    ).add_to(m)

# ----------------------------
# HEATMAPS (DEMAND / SUPPLY / GAP)
# ----------------------------
from folium.plugins import HeatMap

st.subheader("🔥 Heatmaps")

heatmap_type = st.radio(
    "Select Heatmap Type",
    ["Demand", "Supply", "Demand–Supply Gap"],
    horizontal=True,
)

if heatmap_type == "Demand":
    heat_data = district_view[["latitude", "longitude", "total_demand"]].values.tolist()
elif heatmap_type == "Supply":
    heat_data = district_view[["latitude", "longitude", "supply"]].values.tolist()
else:
    heat_data = district_view[["latitude", "longitude", "gap"]].values.tolist()

HeatMap(
    heat_data,
    radius=28,
    blur=20,
    max_zoom=6,
).add_to(m)


# ----------------------------
# DISPLAY MAP
# ----------------------------
st.markdown("### 🗺 Interactive Geo-Map")
st_folium(m, width=1400, height=700)


# ----------------------------
# DATA TABLE
# ----------------------------
st.markdown("---")
st.subheader(f"📊 District-level Summary for: **{selected_skill}**")

st.dataframe(
    district_view[
        ["state", "district", "total_demand", "supply", "gap", "avg_priority"]
    ].sort_values("gap", ascending=False),
    use_container_width=True,
)
