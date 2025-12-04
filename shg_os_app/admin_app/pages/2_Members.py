import streamlit as st
from backend.database import init_db
from backend.shg_ops import get_shgs
from backend.member_ops import get_members, create_member
from components.ui_cards import section_header

init_db()
st.set_page_config(page_title="Members", page_icon="👥", layout="wide")

section_header("Members", "👥", "Onboard and view SHG members")

shgs = get_shgs()
if not shgs:
    st.info("Create an SHG first in the SHG Management page.")
else:
    labels = [f"{name} ({village})" if village else name for (id_, name, village, d, s) in shgs]
    id_map = {labels[i]: shgs[i][0] for i in range(len(shgs))}
    selected = st.selectbox("Select SHG", labels)
    shg_id = id_map[selected]

    st.subheader("Existing Members")
    members = get_members(shg_id)
    if members:
        st.table({
            "ID": [m[0] for m in members],
            "Name": [m[1] for m in members],
            "Phone": [m[2] for m in members],
            "Role": [m[3] for m in members],
        })
    else:
        st.info("No members yet for this SHG.")

    st.markdown("---")
    st.markdown("### ➕ Add Member")

    m_name = st.text_input("Member Name *")
    m_phone = st.text_input("Phone")
    m_role = st.selectbox("Role", ["member", "leader", "treasurer"])

    if st.button("Save Member"):
        if not m_name.strip():
            st.error("Name is required.")
        else:
            create_member(shg_id, m_name.strip(), m_phone.strip(), m_role)
            st.success("Member added.")
            st.rerun()