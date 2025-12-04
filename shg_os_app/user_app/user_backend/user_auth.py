import sqlite3
from backend.database import get_connection


def init_user_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shg_id INTEGER,
            username TEXT UNIQUE,
            password TEXT,
            created_at TEXT
        );
    """)
    conn.commit()
    conn.close()


def register_user(shg_id, username, password):
    conn = get_connection()
    cur = conn.cursor()

    # Check if phone(username) already exists
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    if cur.fetchone():
        conn.close()
        return False, "Phone number already registered!"

    cur.execute(
        "INSERT INTO users (shg_id, username, password) VALUES (?, ?, ?)",
        (shg_id, username, password)
    )
    conn.commit()
    conn.close()
    return True, "Registration successful!"
    


def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, shg_id, username FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return True, {
            "id": row[0],
            "shg_id": row[1],
            "name": row[2],
        }
    else:
        return False, "Invalid phone number or password!"
