import streamlit as st
from pathlib import Path

def load_css():
    css_path = Path(__file__).resolve().parent.parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def glass_card(title, value, subtitle=None, icon=None, color_class="accent"):
    load_css()
    icon_html = f"<span class='metric-icon'>{icon}</span>" if icon else ""
    subtitle_html = f"<div class='metric-subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""<div class="glass-card {color_class}">
                <div class="metric-header">
                    {icon_html}
                    <span class="metric-title">{title}</span>
                </div>
                <div class="metric-value">{value}</div>
                {subtitle_html}
            </div>""", unsafe_allow_html=True
    )

def section_header(title, emoji="✨", subtitle=None):
    load_css()
    sub = f"<div class='section-subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""<div class="section-header">
                <div class="section-title">{emoji} {title}</div>
                {sub}
            </div>""", unsafe_allow_html=True
    )