import streamlit as st
from backend.ai_insight_engine import prepare_insight_bundle, ask_ai_for_insights
from components.ui_cards import section_header, glass_card

st.set_page_config(
    page_title="AI SHG Insight Advisor",
    page_icon="🤖",
    layout="wide",
)

section_header(
    "AI SHG Insight Advisor",
    "🤖",
    "Ask anything about SHG capacity, markets, clusters or opportunities — AI will analyse and answer."
)

st.markdown("### Ask a Question")

user_question = st.text_area(
    "Enter your query (e.g., 'Which SHGs in Gujarat can scale fastest?', 'Where should we target market linkage?')",
    height=100
)

if st.button("Generate Insights"):
    if not user_question.strip():
        st.error("Please enter your question.")
    else:
        with st.spinner("Collecting SHG metrics and generating insights..."):
            bundle = prepare_insight_bundle()
            final_answer = ask_ai_for_insights(user_question, bundle)

        st.markdown("## 🔍 AI Insight Report")
        st.write(final_answer)
