import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "shg_os.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Add missing column if not exists
cur.execute("""
ALTER TABLE shg_production ADD COLUMN product_type TEXT DEFAULT 'non_perishable';
""")

conn.commit()
conn.close()

print("✔ product_type column added successfully!")
