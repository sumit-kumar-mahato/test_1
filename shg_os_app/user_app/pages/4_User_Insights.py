import sys, os
import streamlit as st
import pandas as pd
from datetime import date, timedelta

PHASE2_ROOT = r"C:\Users\sumit\Desktop\IMPACTATHON\PHASE_2"

# Admin backend path
ADMIN_BACKEND = os.path.join(PHASE2_ROOT, "streamlit_app", "backend")
sys.path.insert(0, ADMIN_BACKEND)

# User backend path
USER_BACKEND = os.path.join(PHASE2_ROOT, "user_app", "user_backend")
sys.path.insert(0, USER_BACKEND)

from database import get_connection
import google.generativeai as genai


# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="User Insights Dashboard", page_icon="📊", layout="wide")

if "logged_in" not in st.session_state:
    st.switch_page("pages/1_User_Login.py")

user = st.session_state["user"]
shg_id = user["shg_id"]

st.title(f"📊 Insights Dashboard for {user['name']}")
st.caption(f"SHG ID: {shg_id}")

conn = get_connection()


# -----------------------------------------
# FETCH USER SHG SALES DATA
# -----------------------------------------
df = pd.read_sql_query("""
SELECT 
    u.date,
    u.qty_sold,
    u.qty_produced,
    u.price,
    u.expiry_date,
    p.product_name,
    p.product_type
FROM shg_production_updates u
JOIN shg_production p ON p.id = u.product_id
WHERE u.shg_id = ?
ORDER BY date DESC
""", conn, params=(shg_id,))

if df.empty:
    st.warning("No sales data found. Please update daily product data.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])


# -----------------------------------------
# TABS
# -----------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📌 Overview", "📈 Sales Trends", "🔮 Forecast", "🤖 AI Recommendations"])


# ==========================================================
# TAB 1 — OVERVIEW
# ==========================================================
with tab1:
    st.subheader("📌 Daily Overview")

    today = date.today().isoformat()
    today_df = df[df["date"] == today]

    total_sold = today_df["qty_sold"].sum()
    total_revenue = (today_df["qty_sold"] * today_df["price"]).sum()

    col1, col2 = st.columns(2)
    col1.metric("Today's Quantity Sold", int(total_sold))
    col2.metric("Today's Revenue (₹)", f"{total_revenue:,.0f}")

    # Expiring stock
    expiring = df[df["expiry_date"] == today]
    st.markdown("### ⚠ Expiring Today")
    if expiring.empty:
        st.success("No products expiring today.")
    else:
        st.error(expiring[["product_name", "qty_produced", "expiry_date"]])

    # Best & worst products
    perf = df.groupby("product_name").agg({"qty_sold": "sum"}).sort_values("qty_sold", ascending=False)

    st.markdown("### ⭐ Best Performing Products")
    st.table(perf.head(5))

    st.markdown("### ❗ Weak Products (Need attention)")
    st.table(perf.tail(5))


# ==========================================================
# TAB 2 — SALES TRENDS
# ==========================================================
with tab2:
    st.subheader("📈 Sales Trends")

    trend = df.groupby("date").agg({"qty_sold": "sum", "price": "mean"})
    trend["revenue"] = trend["qty_sold"] * trend["price"]

    st.line_chart(trend[["qty_sold"]], height=300)
    st.caption("Daily Quantity Sold")

    st.line_chart(trend[["revenue"]], height=300)
    st.caption("Daily Revenue (₹)")

    # product-wise trends
    prod_trend = df.groupby(["date", "product_name"])["qty_sold"].sum().unstack().fillna(0)

    st.area_chart(prod_trend, height=300)
    st.caption("Product-wise Sales Trend")


# ==========================================================
# TAB 3 — FORECAST (Simple Moving Average)
# ==========================================================
with tab3:
    st.subheader("🔮 Next 7 Days Forecast")

    last_7 = trend.tail(7)["qty_sold"].mean()
    last_7_rev = trend.tail(7)["revenue"].mean()

    future_dates = [date.today() + timedelta(days=i) for i in range(1, 8)]

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "expected_qty_sold": int(last_7),
        "expected_revenue": int(last_7_rev)
    })

    st.table(forecast_df)


# ==========================================================
# TAB 4 — AI RECOMMENDATIONS
# ==========================================================
with tab4:
    st.subheader("🤖 AI-Powered Recommendations")

    user_question = st.text_area("Ask anything about your SHG performance:")

    if st.button("Get Insights"):
        bundle = {
            "today_revenue": float(total_revenue),
            "today_qty_sold": float(total_sold),
            "best_products": perf.head(3).reset_index().to_dict(orient="records"),
            "weak_products": perf.tail(3).reset_index().to_dict(orient="records"),
            "forecast_next_7_days": forecast_df.to_dict(orient="records"),
        }

        prompt = f"""
You are an SHG business expert. Analyze this user's SHG data and give practical advice.

DATA:
{bundle}

Provide insights on:
- Which products to increase?
- Which products to improve?
- Revenue improvement strategies
- Stock & expiry management
- Demand prediction logic
- Village-level business advice

Be specific and simple.
"""

        # Use same Gemini key from admin app
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-1.5-flash")
        ans = model.generate_content(prompt)

        st.markdown("### 💡 AI Advice")
        st.write(ans.text)