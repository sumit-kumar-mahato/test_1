# user_app/home.py

import sys
from pathlib import Path
import streamlit as st

# -------------------------------------------------------------------
# FIX PATHS → Make sure admin backend + user backend both importable
# -------------------------------------------------------------------

# This file is inside:   PHASE_2/user_app/home.py
BASE_DIR = Path(__file__).resolve().parent                   # /PHASE_2/user_app

# Admin backend location: /PHASE_2/streamlit_app/backend
ADMIN_BACKEND = BASE_DIR.parent / "streamlit_app" / "backend"
sys.path.insert(0, str(ADMIN_BACKEND))

# User backend location: /PHASE_2/user_app/user_backend
USER_BACKEND = BASE_DIR / "user_backend"
sys.path.insert(0, str(USER_BACKEND))

# -------------------------------------------------------------------
# IMPORTS (Now they will work correctly)
# -------------------------------------------------------------------
from database import get_connection          # from admin backend
from user_auth import init_user_table, login_user, register_user


# -------------------------------------------------------------------
# STREAMLIT PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="SHG User Home",
    page_icon="🏠",
    layout="wide"
)

# -------------------------------------------------------------------
# LOGIN CHECK
# -------------------------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("pages/1_User_Login.py")

user = st.session_state["user"]     # stored after login
shg_id = user["shg_id"]

# -------------------------------------------------------------------
# MAIN UI
# -------------------------------------------------------------------
st.title(f"🏠 Welcome, {user['name']}!")
st.write(f"You are part of *SHG ID: {shg_id}*")

st.markdown("---")

st.subheader("What would you like to do today?")

st.write("""
### 🌟 Quick Actions for SHG Members

- 📦 *Update Daily Product Sales*  
  Record today’s production, sales, stock, and price updates.

- 📈 *View Insights Dashboard*  
  AI-driven product performance, price trends, and forecasts.

- 💬 *Join Community Chat*  
  Talk with SHG members across India, share achievements, get help.

- 🙋 *Request Support / Ask for Help*  
  Raise mentorship requests, ask for market connections, or seek training.

- 📰 *Success Stories Feed*  
  Learn from top-performing SHGs to improve your business.

- 🤖 *SHG Chatbot*  
  Ask any question related to business, pricing, government schemes, or SHG growth.
""")

st.markdown("---")

st.success("You are logged in. Use the sidebar to navigate to different sections.")