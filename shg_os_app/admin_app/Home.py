# shg_os_app/admin_app/Home.py

import sys
from pathlib import Path
import streamlit as st

# -----------------------------------------------------
# PACKAGE / IMPORT SETUP
# -----------------------------------------------------
# This file lives in:  shg_os_app/admin_app/Home.py
# We want to import:   admin_app.backend.*  and  admin_app.components.*
# So we add shg_os_app/ to sys.path and import via the package name.

CURRENT_DIR = Path(__file__).resolve().parent         # .../admin_app
APP_ROOT = CURRENT_DIR.parent                         # .../shg_os_app

# Make "admin_app" importable as a package
sys.path.insert(0, str(APP_ROOT))

from admin_app.backend.database import init_db
from admin_app.backend.shg_ops import get_shgs
from admin_app.backend.tx_ops import get_transactions
from admin_app.backend.product_ops import get_products
from admin_app.backend.business_logic import compute_summary_and_advice
from admin_app.components.ui_cards import section_header, glass_card
from admin_app.components.charts import income_expense_chart

# -----------------------------------------------------
# STREAMLIT PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(
    page_title="SHG OS — Admin Dashboard",
    page_icon="🤝",
    layout="wide",
)

# -----------------------------------------------------
# INITIALISE DATABASE
# -----------------------------------------------------
init_db()

# -----------------------------------------------------
# HEADER SECTION
# -----------------------------------------------------
section_header(
    "SHG Business & Credibility OS",
    "🤝",
    "Glassmorphism dashboard for Self-Help Groups",
)

# -----------------------------------------------------
# FETCH SHGs
# -----------------------------------------------------
shgs = get_shgs()

if not shgs:
    st.info("No SHGs found. Please add SHGs from the SHG Management page.")
    st.stop()

# Build labels for dropdown
labels = [
    f"{name} ({village})" if village else name
    for (id_, name, village, district, state) in shgs
]
id_map = {labels[i]: shgs[i][0] for i in range(len(shgs))}

selected_label = st.selectbox(
    "Select SHG to view business snapshot",
    labels,
)

selected_shg_id = id_map[selected_label]

# -----------------------------------------------------
# LOAD TRANSACTIONS & PRODUCTS
# -----------------------------------------------------
txs = get_transactions(selected_shg_id)
products = get_products(selected_shg_id)

(
    total_income,
    total_expense,
    balance,
    score,
    inventory_value,
    rec,
) = compute_summary_and_advice(txs, products)

# -----------------------------------------------------
# TOP KPI CARDS
# -----------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

glass_card(
    "Total Income",
    f"₹{total_income:,.0f}",
    "All-time inflows",
    "💰",
    "accent",
)

glass_card(
    "Total Expense",
    f"₹{total_expense:,.0f}",
    "All-time outflows",
    "📤",
    "accent",
)

glass_card(
    "Net Balance",
    f"₹{balance:,.0f}",
    "Approx cash position",
    "📊",
    "success" if balance >= 0 else "danger",
)

glass_card(
    "Credibility Score",
    f"{score}/100",
    "Financial discipline & consistency",
    "⭐",
    "accent",
)

st.markdown("")

# -----------------------------------------------------
# CASHFLOW TREND
# -----------------------------------------------------
section_header(
    "Cashflow Trend",
    "📈",
    "Income vs expense over time",
)
income_expense_chart(txs)

# -----------------------------------------------------
# INVENTORY + INSIGHTS
# -----------------------------------------------------
section_header(
    "Coach Insight",
    "🧠",
    "Automated observations based on this SHG's data",
)
st.write(rec)