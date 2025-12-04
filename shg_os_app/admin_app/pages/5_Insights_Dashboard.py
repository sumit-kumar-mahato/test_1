import streamlit as st
from backend.database import init_db
from backend.shg_ops import get_shgs
from backend.tx_ops import get_transactions
from backend.product_ops import get_products, get_inventory_for_product
from backend.business_logic import compute_summary_and_advice
from components.ui_cards import section_header, glass_card
from components.charts import income_expense_chart

init_db()
st.set_page_config(page_title="Insights Dashboard", page_icon="📊", layout="wide")

section_header("Insights Dashboard", "📊", "Deeper analytics to guide SHG decisions")

shgs = get_shgs()
if not shgs:
    st.info("Create an SHG first in the SHG Management page.")
else:
    labels = [f"{name} ({village})" if village else name for (id_, name, village, d, s) in shgs]
    id_map = {labels[i]: shgs[i][0] for i in range(len(shgs))}
    selected = st.selectbox("Select SHG", labels)
    shg_id = id_map[selected]

    txs = get_transactions(shg_id)
    products = get_products(shg_id)
    total_income, total_expense, balance, score, inventory_value, rec = compute_summary_and_advice(txs, products)

    c1, c2, c3 = st.columns(3)
    glass_card("Transactions Logged", str(len(txs)), "All-time entries", "🧾")
    glass_card("Inventory Value", f"₹{inventory_value:,.0f}", "At cost price", "📦")
    glass_card("Credibility", f"{score}/100", "Financial discipline", "⭐")

    st.markdown("### Income vs Expense")
    income_expense_chart(txs)

    st.markdown("### Product-wise Stock Snapshot")
    if products:
        table = {"Product": [], "Stock Qty": [], "Unit": []}
        for p in products:
            pid, name, cat, unit, cp, sp = p
            qty = get_inventory_for_product(pid)
            table["Product"].append(name)
            table["Stock Qty"].append(qty)
            table["Unit"].append(unit)
        st.table(table)
    else:
        st.info("No products defined yet.")