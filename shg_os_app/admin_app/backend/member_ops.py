from .database import get_connection
from datetime import datetime

def create_member(shg_id, name, phone, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO member (shg_id, name, phone, role, joined_at) VALUES (?, ?, ?, ?, ?)",
        (shg_id, name, phone, role, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_members(shg_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, phone, role FROM member WHERE shg_id = ? ORDER BY id;",
        (shg_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows