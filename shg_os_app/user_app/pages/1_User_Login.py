import sys
import os
from pathlib import Path
import streamlit as st

# -----------------------------------------------------
# 🔧 FIX PATHS (IMPORTANT)
# -----------------------------------------------------
PHASE2_ROOT = Path(__file__).resolve().parents[1]   # .../PHASE_2

# Admin backend (database + shared tables)
ADMIN_BACKEND = PHASE2_ROOT / "streamlit_app" / "backend"
sys.path.insert(0, str(ADMIN_BACKEND))

# User backend
USER_BACKEND = PHASE2_ROOT / "user_app" / "user_backend"
sys.path.insert(0, str(USER_BACKEND))

# Correct imports
from database import get_connection
from user_auth import init_user_table, register_user, login_user


# -----------------------------------------------------
# 🏁 STREAMLIT PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(page_title="SHG User Login", page_icon="🔐", layout="centered")

# Initialize user table
init_user_table()

st.title("🔐 SHG User Login / Registration")
st.write("Welcome to the SHG User Portal")

# -----------------------------------------------------
# TABS
# -----------------------------------------------------
login_tab, register_tab = st.tabs(["Login", "Register"])


# -----------------------------------------------------
# 🔑 LOGIN TAB
# -----------------------------------------------------
with login_tab:
    st.subheader("Login to Your SHG Dashboard")

    phone = st.text_input("Phone Number", key="login_phone")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login", key="login_btn"):
        ok, response = login_user(phone, password)

        if ok:
            st.success(f"Welcome, {response['name']}!")

            # Save session
            st.session_state["logged_in"] = True
            st.session_state["user"] = response
            st.session_state["shg_id"] = response["shg_id"]

            st.success("Redirecting to Dashboard...")
            st.switch_page("home.py")

        else:
            st.error(response)


# -----------------------------------------------------
# 📝 REGISTER TAB
# -----------------------------------------------------
with register_tab:
    st.subheader("Register as a New SHG Member")

    name = st.text_input("Full Name", key="reg_name")
    phone_r = st.text_input("Phone Number", key="reg_phone")
    password_r = st.text_input("Create Password", type="password", key="reg_pass")

    # Load SHG list from DB
    conn = get_connection()
    rows = conn.execute("SELECT id, name FROM shg").fetchall()
    conn.close()

    shg_map = {row[1]: row[0] for row in rows}

    selected_shg_name = st.selectbox(
        "Select Your SHG",
        list(shg_map.keys()),
        key="reg_shg"
    )
    selected_shg_id = shg_map[selected_shg_name]

    if st.button("Register", key="reg_btn"):
        # correct function signature: (shg_id, phone, password)
        ok, msg = register_user(selected_shg_id, phone_r, password_r)

        if ok:
            st.success(msg)
        else:
            st.error(msg)