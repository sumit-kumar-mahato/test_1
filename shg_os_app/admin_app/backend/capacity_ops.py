from .database import get_connection

def add_capacity(shg_id, product_name, monthly_capacity, supply_ready):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO shg_production (shg_id, product_name, monthly_capacity, supply_ready)
        VALUES (?, ?, ?, ?)
        """,
        (shg_id, product_name, monthly_capacity, supply_ready),
    )
    conn.commit()
    conn.close()

def get_capacity_for_shg(shg_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT product_name, monthly_capacity, supply_ready
        FROM shg_production
        WHERE shg_id = ?
        """,
        (shg_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_capacity():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT shg_id, product_name, monthly_capacity, supply_ready
        FROM shg_production
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows
