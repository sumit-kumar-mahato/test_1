import sqlite3

# Correct relative path to Admin OS DB
DB_PATH = "../../streamlit_app/shg_os.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS shg_production_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shg_id INTEGER,
    product_id INTEGER,
    date TEXT,
    qty_produced REAL,
    qty_sold REAL,
    price REAL,
    expiry_date TEXT,
    notes TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shg_id INTEGER,
    product_id INTEGER,
    tx_date TEXT,
    amount REAL,
    tx_type TEXT,
    quantity REAL,
    description TEXT
);
""")

conn.commit()
conn.close()

print("Database updated with user modules!")
