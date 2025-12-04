import sys, os
import streamlit as st
from datetime import date

# -----------------------------------------------------
# PATH SETUP
# -----------------------------------------------------
PHASE2_ROOT = r"C:\Users\sumit\Desktop\IMPACTATHON\PHASE_2"

ADMIN_ROOT = os.path.join(PHASE2_ROOT, "streamlit_app")
sys.path.insert(0, ADMIN_ROOT)

USER_BACKEND = os.path.join(PHASE2_ROOT, "user_app", "user_backend")
sys.path.insert(0, USER_BACKEND)

from backend.database import get_connection

# -----------------------------------------------------
# CHECK LOGIN
# -----------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("pages/1_User_Login.py")

user = st.session_state["user"]
shg_id = st.session_state["shg_id"]

st.title("📦 Daily Product Update")
st.write(f"Logged in as: **{user['name']}** (SHG ID: {shg_id})")

# -----------------------------------------------------
# GET DB CONNECTION
# -----------------------------------------------------
conn = get_connection()
cur = conn.cursor()

# -----------------------------------------------------
# AUTO-DETECT PRODUCT TYPE COLUMN
# -----------------------------------------------------
cur.execute("PRAGMA table_info(shg_production)")
cols = cur.fetchall()

# Extract only names
col_names = [c[1] for c in cols]

# Find valid product type column
possible_type_cols = ["product_type", "type", "category", "prod_type"]

product_type_col = None
for c in possible_type_cols:
    if c in col_names:
        product_type_col = c
        break

if product_type_col is None:
    st.error("❌ ERROR: No product type column found in shg_production table!")
    st.write("Found columns:", col_names)
    st.stop()

# -----------------------------------------------------
# FETCH PRODUCTS USING CORRECT COLUMN
# -----------------------------------------------------
query = f"""
    SELECT id, product_name, {product_type_col}
    FROM shg_production
    WHERE shg_id = ?
"""

cur.execute(query, (shg_id,))
products = cur.fetchall()

if not products:
    st.warning("Your SHG has no products added yet.")
    conn.close()
    st.stop()

product_map = {f"{p[1]} ({p[2]})": p for p in products}

selected_label = st.selectbox("Select product to update", product_map.keys())

prod_id, prod_name, prod_type = product_map[selected_label]

# -----------------------------------------------------
# INPUT FORM
# -----------------------------------------------------
st.subheader(f"Update for: {prod_name}")

price = st.number_input("Selling Price (₹)", min_value=0.0, step=1.0)
qty_sold = st.number_input("Quantity Sold", min_value=0.0, step=1.0)
qty_produced = st.number_input("Quantity Produced", min_value=0.0, step=1.0)

expiry_date = None
if str(prod_type).lower() == "perishable":
    expiry_date = st.date_input("Expiry Date", min_value=date.today())
else:
    st.info("Non-perishable item — no expiry date needed.")

notes = st.text_area("Notes (optional)")

# -----------------------------------------------------
# SAVE UPDATE
# -----------------------------------------------------
if st.button("💾 Save Today's Update"):
    today = date.today().isoformat()

    cur.execute("""
        INSERT INTO shg_production_updates
        (shg_id, product_id, date, qty_produced, qty_sold, price, expiry_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        shg_id, prod_id, today, qty_produced, qty_sold, price,
        expiry_date.isoformat() if expiry_date else None, notes
    ))

    total_income = price * qty_sold

    cur.execute("""
        INSERT INTO tx
        (shg_id, member_id, product_id, tx_date, quantity, amount, tx_type, description)
        VALUES (?, NULL, ?, ?, ?, ?, ?, ?)
    """, (
        shg_id, prod_id, today, qty_sold, total_income,
        "sale", f"Daily update: {prod_name}"
    ))

    conn.commit()
    conn.close()

    st.success("Update saved successfully!")
    st.balloons()
