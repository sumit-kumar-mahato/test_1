from .database import get_connection

def add_transaction(shg_id, member_id, product_id, tx_date, quantity, amount, tx_type, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tx (shg_id, member_id, product_id, tx_date, quantity, amount, tx_type, description) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (shg_id, member_id, product_id, tx_date, quantity, amount, tx_type, description)
    )
    conn.commit()
    conn.close()

def get_transactions(shg_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, tx_date, amount, tx_type, description, product_id, quantity FROM tx WHERE shg_id = ? ORDER BY tx_date;",
        (shg_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows