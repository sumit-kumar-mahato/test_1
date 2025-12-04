from .database import get_connection
from datetime import datetime

def create_product(shg_id, name, category, unit, cost_price, selling_price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO product (shg_id, name, category, unit, cost_price, selling_price, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (shg_id, name, category, unit, cost_price, selling_price, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_products(shg_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, category, unit, cost_price, selling_price FROM product WHERE shg_id = ? ORDER BY id;",
        (shg_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_inventory_for_product(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT quantity FROM inventory WHERE product_id = ? ORDER BY id DESC LIMIT 1;",
        (product_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0.0

def update_inventory(product_id, quantity_change):
    current_qty = get_inventory_for_product(product_id)
    new_qty = current_qty + quantity_change
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO inventory (product_id, quantity, updated_at) VALUES (?, ?, ?)",
        (product_id, new_qty, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()