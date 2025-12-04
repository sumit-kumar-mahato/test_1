import streamlit as st
from backend.deployment_engine import match_shgs_to_demand
from components.ui_cards import section_header, glass_card

st.set_page_config(
    page_title="SHG Deployment Engine",
    page_icon="🚚",
    layout="wide",
)

section_header(
    "SHG Deployment Engine",
    "🚚",
    "Match demand with the best possible SHGs based on skills, supply, capacity and financial stability."
)

st.markdown("### Enter Demand Details")

col1, col2, col3 = st.columns(3)
location = col1.text_input("Location Name")
district = col2.text_input("District")
state = col3.text_input("State")

product_required = st.text_input("Product Required")
qty_required = st.number_input("Required Quantity", min_value=1, step=10)

if st.button("Find Best SHG Matches"):
    if not product_required or qty_required <= 0:
        st.error("Please enter required product and quantity.")
    else:
        result_df, err = match_shgs_to_demand(
            location, district, state,
            product_required, qty_required
        )

        if err:
            st.warning(err)
        else:
            st.success("Best SHG Matches Found!")

            st.dataframe(
                result_df[[
                    "shg_id", "name", "district", "state",
                    "product_name", "total_capacity", "total_supply_ready",
                    "avg_income", "match_score"
                ]],
                use_container_width=True
            )

            best = result_df.iloc[0]
            glass_card(
                "Top Recommended SHG",
                best["name"],
                f"Match Score: {best['match_score']}%",
                "🏆"
            )
