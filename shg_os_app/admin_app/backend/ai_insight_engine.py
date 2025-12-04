import streamlit as st
import pandas as pd
import json
import time
import random
import google.generativeai as genai

from backend.clustering_engine import compute_shg_clusters
from backend.shg_health_engine import compute_shg_health
from backend.insights_engine import (
    get_underutilized_shgs,
    get_high_potential_low_income_shgs,
    get_top_products_by_capacity,
)
from backend.database import get_connection
from backend.safe_utils import safe_float


# ---------- GEMINI CONFIG ----------
API_KEY = st.secrets.get("GEMINI_API_KEY", None)

if not API_KEY:
    st.error("❌ GEMINI_API_KEY not found in .streamlit/secrets.toml")
else:
    genai.configure(api_key=API_KEY)


# ---------- LOAD BASE SHG INFO ----------
def load_shg_base():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id AS shg_id, name, village, district, state FROM shg;",
        conn,
    )
    conn.close()
    return df


# ---------- PREPARE INSIGHT BUNDLE ----------
def prepare_insight_bundle():
    base = load_shg_base()
    clusters, summary = compute_shg_clusters(6)
    health_df, health_summary = compute_shg_health()

    under_df = get_underutilized_shgs()
    high_pot = get_high_potential_low_income_shgs()
    top_prod = get_top_products_by_capacity()

    bundle = {
        "total_shgs": len(base),
        "cluster_summary": summary.to_dict(orient="records") if not summary.empty else [],
        "health_summary": health_summary.to_dict(orient="records") if not health_summary.empty else [],
        "underutilised": under_df.to_dict(orient="records") if not under_df.empty else [],
        "high_potential": high_pot.to_dict(orient="records") if not high_pot.empty else [],
        "top_products": top_prod.to_dict(orient="records") if not top_prod.empty else [],
    }

    return bundle


# ---------- SAFE GEMINI CALL ----------
def safe_generate(model, prompt, retries=5):
    for attempt in range(retries):
        try:
            return model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 600,
                    "temperature": 0.2,
                }
            )
        except Exception as e:
            msg = str(e)

            # Handle rate limits
            if ("Resource exhausted" in msg or "429" in msg) and attempt < retries - 1:
                time.sleep((2 ** attempt) + random.random())
                continue

            return f"❌ Gemini Error: {msg}"

    return "❌ Gemini failed repeatedly."


# ---------- MAIN AI ENGINE ----------
def ask_ai_for_insights(user_query, bundle):
    if not API_KEY:
        return "⚠️ GEMINI_API_KEY is not configured."

    # Reduce payload to avoid 429
    bundle["underutilised"] = bundle["underutilised"][:20]
    bundle["high_potential"] = bundle["high_potential"][:20]
    bundle["top_products"] = bundle["top_products"][:20]

    compact_json = json.dumps(bundle, separators=(",", ":"))

    prompt = f"""
You are an expert in SHG livelihood, rural development, cluster management and market linkage.

SHG System Data (JSON):
{compact_json}

User Query:
\"{user_query}\"

Give practical, SHG-specific insights:
- Opportunities
- Risks
- Target SHGs/clusters
- Buyer linkages
- Recommended actions
    """

    # ✔ Correct model for your SDK (v1)
    model = genai.GenerativeModel("gemini-2.0-flash")

    resp = safe_generate(model, prompt)

    if isinstance(resp, str):
        return resp

    return resp.text if hasattr(resp, "text") else "⚠️ No response from Gemini."
