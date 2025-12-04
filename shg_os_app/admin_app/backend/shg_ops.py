from .database import get_connection
from datetime import datetime

def create_shg(name, village, district, state):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO shg (name, village, district, state, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, village, district, state, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_shgs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, village, district, state FROM shg ORDER BY id DESC;")
    rows = cur.fetchall()
    conn.close()
    return rows