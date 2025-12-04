from .product_ops import get_inventory_for_product
from backend.safe_utils import safe_float


def safe_float(x):
    try:
        return float(x)
    except:
        return 0.0


def compute_summary_and_advice(transactions, products):
    total_income = 0.0
    total_expense = 0.0

    for _id, tx_date, amount, tx_type, desc, product_id, qty in transactions:
        if tx_type in ["income", "loan_repaid", "savings", "sale"]:
            total_income += safe_float(amount)
        elif tx_type in ["expense", "loan_disbursed", "purchase"]:
            total_expense += safe_float(amount)

    balance = total_income - total_expense
    num_txs = len(transactions)

    score = 50
    if balance >= 0:
        score = 65
        if num_txs >= 10:
            score = 75
        if num_txs >= 20 and balance > 0:
            score = 82
    else:
        score = 45

    inventory_value = 0.0
    for p in products:
        p_id, name, category, unit, cost_price, selling_price = p
        qty = get_inventory_for_product(p_id)
        cp = safe_float(cost_price)
        inventory_value += qty * cp

    if balance < 0:
        rec = "Your expenses are higher than income. Reduce non-essential spending and increase income-generating activities."
    elif balance >= 0 and inventory_value > 0 and inventory_value > (balance * 2):
        rec = "You are holding a lot of inventory. Focus on selling existing stock before producing more."
    elif balance >= 0 and num_txs < 5:
        rec = "Good surplus, but very few transactions recorded. Train members to log every sale, purchase, and expense."
    else:
        rec = "Great job maintaining a surplus. Consider reinvesting part of it into your most profitable products."

    return total_income, total_expense, balance, score, inventory_value, rec