from datetime import datetime
from .database import get_connection

def add_demand(location, district, state, product_required, quantity_required, deadline):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO demand_centers
        (location, district, state, product_required, quantity_required, deadline, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            location,
            district,
            state,
            product_required,
            quantity_required,
            deadline,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

def get_all_demand():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, location, district, state, product_required, quantity_required, deadline
        FROM demand_centers
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows
