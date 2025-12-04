import streamlit as st
import pandas as pd

from backend.collaboration_engine import (
    get_available_products,
    suggest_collaboration_teams,
)
from components.ui_cards import section_header, glass_card

st.set_page_config(
    page_title="SHG Collaboration Engine",
    page_icon="🤝",
    layout="wide",
)

section_header(
    "SHG Collaboration Engine",
    "🤝",
    "Form multi-SHG teams to fulfil large orders by combining capacity across groups."
)

# ---- Input Form ----
st.markdown("### Define Bulk Order Requirements")

products = get_available_products()
col1, col2 = st.columns(2)

if products:
    product_required = col1.selectbox("Select Product", options=products)
else:
    product_required = col1.text_input("Product Name (no products detected in DB)")

qty_required = col2.number_input("Required Quantity (units)", min_value=1, step=50)

loc_col1, loc_col2 = st.columns(2)
state_filter = loc_col1.text_input("Preferred State (optional)")
district_filter = loc_col2.text_input("Preferred District (optional)")

max_team_size = st.slider("Maximum SHGs per team", min_value=1, max_value=4, value=4)
top_k = st.slider("Number of team suggestions", min_value=1, max_value=10, value=5)

if st.button("Suggest SHG Teams"):
    if not product_required:
        st.error("Please select or enter a product name.")
    else:
        teams, base_df, msg = suggest_collaboration_teams(
            product_required=product_required,
            qty_required=qty_required,
            state_filter=state_filter,
            district_filter=district_filter,
            max_team_size=max_team_size,
            top_k=top_k,
        )

        if msg:
            st.warning(msg)
        else:
            st.success("Collaboration teams generated successfully!")

            # ---- Summary table of teams ----
            summary_rows = []
            for t in teams:
                summary_rows.append(
                    {
                        "Team Rank": t["team_rank"],
                        "Team Size": t["team_size"],
                        "SHGs": ", ".join(t["shg_names"]),
                        "Total Supply Ready": t["total_supply_ready"],
                        "Total Capacity": t["total_capacity"],
                        "Score": t["score"],
                    }
                )

            summary_df = pd.DataFrame(summary_rows)
            st.markdown("### Suggested Teams")
            st.dataframe(summary_df, use_container_width=True)

            # ---- Highlight the best team ----
            best = teams[0]
            col_a, col_b, col_c = st.columns(3)
            glass_card(
                "Top Team Score",
                f"{best['score']} / 100",
                "Higher = better fulfilment, capacity & simplicity",
                "🏆",
            )
            glass_card(
                "Total Supply Ready",
                f"{best['total_supply_ready']:.0f} units",
                f"vs required {qty_required} units",
                "📦",
            )
            glass_card(
                "Team Size",
                f"{best['team_size']} SHGs",
                ", ".join(best["shg_names"]),
                "👥",
            )

            # ---- Detailed view for each team ----
            st.markdown("---")
            st.markdown("### Team Details")

            selected_rank = st.selectbox(
                "View details for team:",
                options=[t["team_rank"] for t in teams],
                format_func=lambda x: f"Team {x}",
            )

            team = next(t for t in teams if t["team_rank"] == selected_rank)

            st.markdown(f"#### Team {team['team_rank']} — {', '.join(team['shg_names'])}")

            detail_rows = []
            for shg_id, shg_name in zip(team["shg_ids"], team["shg_names"]):
                subset = base_df[base_df["shg_id"] == shg_id].iloc[0]
                detail_rows.append(
                    {
                        "SHG Name": shg_name,
                        "Village": subset["village"],
                        "District": subset["district"],
                        "State": subset["state"],
                        "Product": subset["product_name"],
                        "Capacity (units)": subset["monthly_capacity"],
                        "Supply Ready (units)": subset["supply_ready"],
                    }
                )

            detail_df = pd.DataFrame(detail_rows)
            st.dataframe(detail_df, use_container_width=True)
