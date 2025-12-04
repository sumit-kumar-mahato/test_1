import streamlit as st
from datetime import date

from backend.database import init_db
from backend.shg_ops import get_shgs
from backend.product_ops import get_products, create_product, get_inventory_for_product, update_inventory
from backend.tx_ops import add_transaction
from components.ui_cards import section_header

init_db()
st.set_page_config(page_title="Products & Inventory", page_icon="📦", layout="wide")

section_header("Products & Inventory", "📦", "Configure products and manage stock levels")

shgs = get_shgs()
if not shgs:
    st.info("Create an SHG first in the SHG Management page.")
else:
    labels = [f"{name} ({village})" if village else name for (id_, name, village, d, s) in shgs]
    id_map = {labels[i]: shgs[i][0] for i in range(len(shgs))}
    selected = st.selectbox("Select SHG", labels)
    shg_id = id_map[selected]

    st.subheader("Product Catalogue")
    products = get_products(shg_id)
    if products:
        table = {"ID": [], "Name": [], "Category": [], "Unit": [], "Cost Price": [], "Selling Price": [], "Stock Qty": []}
        for p in products:
            pid, name, cat, unit, cp, sp = p
            qty = get_inventory_for_product(pid)
            table["ID"].append(pid)
            table["Name"].append(name)
            table["Category"].append(cat)
            table["Unit"].append(unit)
            table["Cost Price"].append(cp)
            table["Selling Price"].append(sp)
            table["Stock Qty"].append(qty)
        st.table(table)
    else:
        st.info("No products yet.")

    st.markdown("---")
    st.markdown("### ➕ Add Product")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Product Name *")
        category = st.text_input("Category")
        unit = st.text_input("Unit (e.g., piece, kg)")
    with col2:
        cp = st.number_input("Cost Price per Unit (₹)", min_value=0.0, step=1.0)
        sp = st.number_input("Selling Price per Unit (₹)", min_value=0.0, step=1.0)

    if st.button("Save Product"):
        if not name.strip():
            st.error("Product name is required.")
        else:
            create_product(shg_id, name.strip(), category.strip(), unit.strip(), cp, sp)
            st.success("Product added.")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔄 Adjust Inventory")

    products2 = get_products(shg_id)
    if products2:
        label_map = {f"{p[1]} (ID {p[0]})": p[0] for p in products2}
        prod_label = st.selectbox("Select Product", list(label_map.keys()))
        prod_id = label_map[prod_label]
        current_qty = get_inventory_for_product(prod_id)
        st.write(f"Current stock: **{current_qty}**")

        qty_change = st.number_input("Quantity change (+ add / - remove)", step=1.0)
        reason = st.selectbox("Reason", ["production_add", "damage", "adjustment"])

        if st.button("Apply Change"):
            update_inventory(prod_id, qty_change)
            add_transaction(shg_id, None, prod_id, date.today().isoformat(), qty_change, 0.0,
                            f"inventory_{reason}", f"Inventory adjustment: {reason}")
            st.success("Inventory updated.")
            st.rerun()
    else:
        st.info("Add a product first to manage inventory.")