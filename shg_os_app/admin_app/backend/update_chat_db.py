import sqlite3
from pathlib import Path

# -----------------------------------------
# Path to your main SHG database
# -----------------------------------------
DB_PATH = Path(r"C:\Users\sumit\Desktop\IMPACTATHON\PHASE_2\streamlit_app\shg_os.db")

print("Using DB:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# -----------------------------------------
# Create Community Chat table
# -----------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS community_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    shg_id INTEGER,
    message TEXT,
    media_path TEXT,
    media_type TEXT,         -- image / video / file / None
    is_admin INTEGER DEFAULT 0,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("✅ Chat DB updated successfully. Table `community_chat` is ready.")
