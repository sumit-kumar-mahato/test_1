import streamlit as st
from backend.database import init_db
from backend.shg_ops import create_shg, get_shgs
from components.ui_cards import section_header

init_db()
st.set_page_config(page_title="SHG Management", page_icon="🏠", layout="wide")

section_header("SHG Management", "🏠", "Create and manage Self-Help Groups")

with st.form("create_shg_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("SHG Name *")
        village = st.text_input("Village")
        district = st.text_input("District")
    with col2:
        state = st.text_input("State")
        submit = st.form_submit_button("Create SHG")

    if submit:
        if not name.strip():
            st.error("SHG name is required.")
        else:
            create_shg(name.strip(), village.strip(), district.strip(), state.strip())
            st.success("SHG created successfully.")
            st.rerun()

st.markdown("---")
section_header("Existing SHGs", "📋")
rows = get_shgs()
if rows:
    st.table({
        "ID": [r[0] for r in rows],
        "Name": [r[1] for r in rows],
        "Village": [r[2] for r in rows],
        "District": [r[3] for r in rows],
        "State": [r[4] for r in rows],
    })
else:
    st.info("No SHGs created yet.")