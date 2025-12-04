import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "shg_os.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ---- RULES FOR AUTO-CATEGORIZATION ----
perishables = ["milk", "curd", "paneer", "vegetable", "fruit", "pickle", "food", "snack"]
non_perishables = ["bag", "chair", "dress", "toy", "handicraft", "wood", "soap"]

# Fetch all products
rows = cur.execute("SELECT id, product_name FROM shg_production").fetchall()

for pid, name in rows:
    pname = name.lower()

    # Classify
    if any(w in pname for w in perishables):
        ptype = "perishable"
    else:
        ptype = "non_perishable"

    cur.execute("UPDATE shg_production SET product_type = ? WHERE id = ?", (ptype, pid))

conn.commit()
conn.close()

print("✔ Product type updated for all products!")
