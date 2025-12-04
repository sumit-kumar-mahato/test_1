import streamlit as st
from backend.database import init_db
from backend.shg_ops import get_shgs
from backend.member_ops import get_members
from backend.skills_ops import (
    add_skill,
    get_skills_for_member,
    get_all_skilled_members,
    upsert_member_financials,
    get_financials_for_member,
)
from backend.capacity_ops import (
    add_capacity,
    get_capacity_for_shg,
    get_all_capacity,
)
from backend.demand_ops import add_demand, get_all_demand
from components.ui_cards import section_header, glass_card

init_db()
st.set_page_config(page_title="Skill & Deployment Engine", page_icon="🧠", layout="wide")

section_header(
    "Skill & Deployment Engine",
    "🧠",
    "Map SHG skills, capacity and external demand to decide who to club and where to deploy."
)

shgs = get_shgs()
if not shgs:
    st.info("Create at least one SHG in the SHG Management page first.")
    st.stop()

# ---------- Select SHG & Member ----------

labels = [f"{name} ({village})" if village else name for (id_, name, village, d, s) in shgs]
id_map = {labels[i]: shgs[i][0] for i in range(len(shgs))}
selected_shg_label = st.selectbox("Select SHG", labels)
selected_shg_id = id_map[selected_shg_label]

members = get_members(selected_shg_id)
member_map = {f"{m[1]} (ID {m[0]})": m[0] for m in members} if members else {}

col_left, col_right = st.columns(2)

# ---------- LEFT: Member Skills & Financials ----------

with col_left:
    st.subheader("Member Skills & Financial Profile")

    if not members:
        st.info("No members yet for this SHG. Add members first.")
    else:
        selected_member_label = st.selectbox("Select Member", list(member_map.keys()))
        member_id = member_map[selected_member_label]

        st.markdown("**Existing Skills**")
        skills = get_skills_for_member(member_id)
        if skills:
            st.table(
                {
                    "Skill Category": [s[0] for s in skills],
                    "Sub-skill": [s[1] for s in skills],
                    "Years Experience": [s[2] for s in skills],
                }
            )
        else:
            st.info("No skills recorded yet for this member.")

        st.markdown("### ➕ Add / Update Skill")
        skill_cat = st.text_input("Skill Category (e.g., Tailoring, Food Processing)")
        sub_skill = st.text_input("Sub-skill (e.g., School uniforms, Pickle making)")
        years_exp = st.number_input("Years of Experience", min_value=0.0, max_value=50.0, step=0.5)

        if st.button("Save Skill"):
            if not skill_cat.strip():
                st.error("Skill category is required.")
            else:
                add_skill(member_id, skill_cat.strip(), sub_skill.strip(), years_exp)
                st.success("Skill saved.")
                st.rerun()

        st.markdown("---")
        st.markdown("### 💰 Financial Snapshot (Member-level)")

        existing_fin = get_financials_for_member(member_id)
        if existing_fin:
            mi, me, co, lrr, sav = existing_fin
            glass_card("Monthly Income", f"₹{mi:,.0f}", icon="📈")
            glass_card("Monthly Expense", f"₹{me:,.0f}", icon="📉")
            glass_card("Outstanding Credit", f"₹{co:,.0f}", icon="💳")
        else:
            st.info("No financial record yet. Fill the form below.")

        st.markdown("#### Update Financials")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            monthly_income = st.number_input("Monthly Income (₹)", min_value=0.0, step=500.0)
            monthly_expense = st.number_input("Monthly Expense (₹)", min_value=0.0, step=500.0)
        with f_col2:
            credit_outstanding = st.number_input("Outstanding Credit (₹)", min_value=0.0, step=500.0)
            loan_repayment_rate = st.slider("Loan Repayment Rate (0–100%)", 0, 100, 80)
            savings = st.number_input("Savings (₹)", min_value=0.0, step=500.0)

        if st.button("Save Financial Profile"):
            upsert_member_financials(
                member_id,
                monthly_income,
                monthly_expense,
                credit_outstanding,
                loan_repayment_rate / 100.0,
                savings,
            )
            st.success("Financial profile saved.")
            st.rerun()

# ---------- RIGHT: SHG Capacity & Demand Matching ----------

with col_right:
    st.subheader("SHG Production Capacity")

    capacity_rows = get_capacity_for_shg(selected_shg_id)
    if capacity_rows:
        st.table(
            {
                "Product": [r[0] for r in capacity_rows],
                "Monthly Capacity": [r[1] for r in capacity_rows],
                "Supply Ready": [r[2] for r in capacity_rows],
            }
        )
    else:
        st.info("No capacity data for this SHG yet.")

    st.markdown("### ➕ Add / Update Capacity")
    cap_product = st.text_input("Product Name (e.g., paper bags, pickles)")
    cap_monthly = st.number_input("Monthly Capacity (units)", min_value=0.0, step=10.0)
    cap_ready = st.number_input("Supply Ready (units)", min_value=0.0, step=10.0)

    if st.button("Save Capacity"):
        if not cap_product.strip():
            st.error("Product name is required.")
        else:
            add_capacity(selected_shg_id, cap_product.strip(), cap_monthly, cap_ready)
            st.success("Capacity saved.")
            st.rerun()

st.markdown("---")
section_header("External Demand & Deployment Suggestions", "📍")

demand_col, match_col = st.columns(2)

with demand_col:
    st.markdown("### ➕ Add Demand Center")

    loc = st.text_input("Location (e.g., Ahmedabad city)")
    dist = st.text_input("District")
    state = st.text_input("State")
    product_required = st.text_input("Product Required (e.g., paper bags)")
    qty_required = st.number_input("Quantity Required (units)", min_value=0.0, step=50.0)
    deadline = st.date_input("Deadline")

    if st.button("Save Demand"):
        if not product_required.strip():
            st.error("Product required is mandatory.")
        else:
            add_demand(
                loc.strip(),
                dist.strip(),
                state.strip(),
                product_required.strip(),
                qty_required,
                deadline.isoformat(),
            )
            st.success("Demand added.")
            st.rerun()

    st.markdown("### Existing Demand")
    demands = get_all_demand()
    if demands:
        st.table(
            {
                "ID": [d[0] for d in demands],
                "Location": [d[1] for d in demands],
                "District": [d[2] for d in demands],
                "State": [d[3] for d in demands],
                "Product": [d[4] for d in demands],
                "Qty": [d[5] for d in demands],
                "Deadline": [d[6] for d in demands],
            }
        )
    else:
        st.info("No demands recorded yet.")

with match_col:
    st.markdown("### 🔍 Simple Matching: Who can fulfil which demand?")

    all_capacity = get_all_capacity()
    all_demands = get_all_demand()

    if not all_capacity or not all_demands:
        st.info("Need at least one demand and one SHG capacity to show matches.")
    else:
        # Very simple rule-based matching:
        # Match by product name (case-insensitive contains) and capacity >= required
        matches = []
        for d in all_demands:
            d_id, d_loc, d_dist, d_state, d_prod, d_qty, d_deadline = d
            for cap in all_capacity:
                cap_shg_id, cap_prod_name, cap_monthly, cap_ready = cap
                if d_prod.lower() in cap_prod_name.lower() and cap_ready >= d_qty:
                    # find SHG name
                    shg_name = next((name for (sid, name, v, di, stt) in shgs if sid == cap_shg_id), f"SHG {cap_shg_id}")
                    matches.append(
                        {
                            "Demand ID": d_id,
                            "Demand Product": d_prod,
                            "Demand Qty": d_qty,
                            "Location": d_loc,
                            "SHG": shg_name,
                            "SHG Product": cap_prod_name,
                            "Supply Ready": cap_ready,
                        }
                    )

        if matches:
            st.table(matches)
            st.caption("These SHGs can be deployed to these demand centers based on product match & capacity.")
        else:
            st.warning("No exact matches found yet. Try aligning product names and capacities.")
