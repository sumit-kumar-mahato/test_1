import sys, os

PHASE2_ROOT = r"C:\Users\sumit\Desktop\IMPACTATHON\PHASE_2"

# ADMIN BACKEND (for database, clustering, insights etc.)
ADMIN_BACKEND = os.path.join(PHASE2_ROOT, "streamlit_app", "backend")
sys.path.insert(0, ADMIN_BACKEND)

# USER BACKEND (auth, user operations)
USER_BACKEND = os.path.join(PHASE2_ROOT, "user_app", "user_backend")
sys.path.insert(0, USER_BACKEND)

# Imports
from database import get_connection          # from admin backend
from user_backend.user_auth import init_user_table, register_user, login_user


import streamlit as st
import pandas as pd


st.set_page_config(page_title="SHG Directory", page_icon="📘", layout="wide")

if "logged_in" not in st.session_state:
    st.switch_page("pages/1_User_Login.py")

st.title("📘 SHG Directory")
st.caption("Explore SHGs across India: members, products, capacity & more")

conn = get_connection()
cur = conn.cursor()

# ---------------------------------------
# FETCH SHG BASIC DATA
# ---------------------------------------
shgs = pd.read_sql_query("""
SELECT id AS shg_id, name, village, district, state
FROM shg
ORDER BY state, district;
""", conn)

# ---------------------------------------
# MEMBERS COUNT PER SHG
# ---------------------------------------
member_counts = pd.read_sql_query("""
SELECT shg_id, COUNT(*) AS members
FROM member
GROUP BY shg_id;
""", conn)

shgs = shgs.merge(member_counts, on="shg_id", how="left")
shgs["members"] = shgs["members"].fillna(0).astype(int)

# ---------------------------------------
# PRODUCTS PER SHG
# ---------------------------------------
products = pd.read_sql_query("""
SELECT shg_id, product_name, product_type, monthly_capacity, supply_ready
FROM shg_production;
""", conn)

# Group products
product_group = (
    products.groupby("shg_id")
    .agg({
        "product_name": lambda x: ", ".join(x.unique()),
        "product_type": lambda x: ", ".join(x.unique()),
        "monthly_capacity": "sum",
        "supply_ready": "sum"
    })
    .reset_index()
)

shgs = shgs.merge(product_group, on="shg_id", how="left")

# Fill missing fields
shgs["product_name"] = shgs["product_name"].fillna("No products added")
shgs["product_type"] = shgs["product_type"].fillna("-")
shgs["monthly_capacity"] = shgs["monthly_capacity"].fillna(0).astype(int)
shgs["supply_ready"] = shgs["supply_ready"].fillna(0).astype(int)

# Search bar
search = st.text_input("🔍 Search SHG (name, village, district, state or product)")

if search.strip():
    s = search.lower()
    shgs = shgs[
        shgs.apply(lambda row:
                   s in str(row["name"]).lower()
                   or s in str(row["village"]).lower()
                   or s in str(row["district"]).lower()
                   or s in str(row["state"]).lower()
                   or s in str(row["product_name"]).lower(),
                   axis=1)
    ]

st.write(f"### Total SHGs found: {len(shgs)}")

# ---------------------------------------
# DISPLAY DIRECTORY TABLE
# ---------------------------------------
st.dataframe(
    shgs.rename(columns={
        "name": "SHG Name",
        "village": "Village",
        "district": "District",
        "state": "State",
        "members": "Members",
        "product_name": "Products",
        "product_type": "Product Type",
        "monthly_capacity": "Total Capacity",
        "supply_ready": "Supply Ready",
    }),
    use_container_width=True,
)

# ---------------------------------------
# SHG DETAIL VIEW
# ---------------------------------------
st.markdown("---")
st.subheader("🔎 View SHG Details")

selected_id = st.selectbox(
    "Select SHG to view details",
    shgs["shg_id"].tolist()
)

if selected_id:
    st.markdown("### 📘 SHG Full Details")

    # Basic Info
    info = shgs[shgs["shg_id"] == selected_id].iloc[0]
    st.write(f"**Name:** {info['name']}")
    st.write(f"**Location:** {info['village']}, {info['district']}, {info['state']}")
    st.write(f"**Members:** {info['members']}")
    st.write(f"**Products:** {info['product_name']}")
    st.write(f"**Types:** {info['product_type']}")
    st.write(f"**Capacity:** {info['monthly_capacity']} units")
    st.write(f"**Supply Ready:** {info['supply_ready']} units")

    st.markdown("---")
    st.subheader("👥 Members")

    members = pd.read_sql_query("""
    SELECT name, phone, role
    FROM member
    WHERE shg_id = ?
    """, conn, params=(selected_id,))

    st.table(members)

    st.markdown("---")
    st.subheader("📦 Product Details")

    prod = pd.read_sql_query("""
    SELECT product_name, product_type, monthly_capacity, supply_ready
    FROM shg_production
    WHERE shg_id = ?
    """, conn, params=(selected_id,))

    st.table(prod)

conn.close()
