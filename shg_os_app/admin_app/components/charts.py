import streamlit as st
import pandas as pd
from .ui_cards import load_css

def income_expense_chart(transactions):
    load_css()
    if not transactions:
        st.info("Not enough data to show chart yet.")
        return

    rows = []
    for _id, tx_date, amount, tx_type, desc, product_id, qty in transactions:
        rows.append({"date": tx_date, "amount": float(amount), "type": tx_type})

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["category"] = df["type"].apply(
        lambda t: "Income" if t in ["income", "loan_repaid", "savings", "sale"] else "Expense"
    )

    pivot = df.pivot_table(index="date", columns="category", values="amount",
                           aggfunc="sum", fill_value=0).reset_index()

    st.line_chart(pivot.set_index("date"), height=260)