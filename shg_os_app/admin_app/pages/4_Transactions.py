import streamlit as st
from datetime import date

from backend.database import init_db
from backend.shg_ops import get_shgs
from backend.product_ops import get_products, update_inventory
from backend.tx_ops import add_transaction, get_transactions
from components.ui_cards import section_header

init_db()
st.set_page_config(page_title="Transactions", page_icon="💰", layout="wide")

section_header("Transactions / Cashbook", "💰", "Record income, expenses, loans, sales and purchases")

shgs = get_shgs()
if not shgs:
    st.info("Create an SHG first in the SHG Management page.")
else:
    labels = [f"{name} ({village})" if village else name for (id_, name, village, d, s) in shgs]
    id_map = {labels[i]: shgs[i][0] for i in range(len(shgs))}
    selected = st.selectbox("Select SHG", labels)
    shg_id = id_map[selected]

    st.subheader("Existing Transactions")
    txs = get_transactions(shg_id)
    if txs:
        display = {"Date": [], "Type": [], "Amount": [], "Product ID": [], "Qty": [], "Description": []}
        for _id, tx_date, amount, tx_type, desc, product_id, qty in txs:
            display["Date"].append(tx_date)
            display["Type"].append(tx_type)
            display["Amount"].append(amount)
            display["Product ID"].append(product_id)
            display["Qty"].append(qty)
            display["Description"].append(desc)
        st.table(display)
    else:
        st.info("No transactions yet.")

    st.markdown("---")
    st.markdown("### ➕ Add Transaction")

    col1, col2 = st.columns(2)
    with col1:
        tx_date = st.date_input("Date", value=date.today())
        tx_type = st.selectbox(
            "Type",
            ["income", "expense", "loan_disbursed", "loan_repaid", "savings", "sale", "purchase"],
        )
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)

    with col2:
        products = get_products(shg_id)
        link_to_product = st.checkbox("Link to product (for sale/purchase)")
        product_id = None
        qty = 0.0
        if link_to_product and products:
            label_map = {f"{p[1]} (ID {p[0]})": p[0] for p in products}
            prod_label = st.selectbox("Product", list(label_map.keys()))
            product_id = label_map[prod_label]
            qty = st.number_input("Quantity", min_value=0.0, step=1.0)

    desc = st.text_input("Description")

    if st.button("Save Transaction"):
        if amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            if product_id is not None and qty:
                if tx_type == "sale":
                    update_inventory(product_id, -qty)
                elif tx_type == "purchase":
                    update_inventory(product_id, qty)

            add_transaction(shg_id, None, product_id, tx_date.isoformat(), qty, amount, tx_type, desc.strip())
            st.success("Transaction recorded.")
            st.rerun()