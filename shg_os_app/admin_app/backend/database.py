import sqlite3
from datetime import datetime
from pathlib import Path
from backend.safe_utils import safe_float


DB_PATH = Path(__file__).resolve().parent.parent / "shg_os.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS shg (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            village TEXT,
            district TEXT,
            state TEXT,
            created_at TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS member (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shg_id INTEGER,
            name TEXT NOT NULL,
            phone TEXT,
            role TEXT,
            joined_at TEXT,
            FOREIGN KEY (shg_id) REFERENCES shg(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shg_id INTEGER,
            name TEXT NOT NULL,
            category TEXT,
            unit TEXT,
            cost_price REAL,
            selling_price REAL,
            created_at TEXT,
            FOREIGN KEY (shg_id) REFERENCES shg(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity REAL,
            updated_at TEXT,
            FOREIGN KEY (product_id) REFERENCES product(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tx (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shg_id INTEGER,
            member_id INTEGER,
            product_id INTEGER,
            tx_date TEXT,
            quantity REAL,
            amount REAL,
            tx_type TEXT,
            description TEXT,
            FOREIGN KEY (shg_id) REFERENCES shg(id),
            FOREIGN KEY (member_id) REFERENCES member(id),
            FOREIGN KEY (product_id) REFERENCES product(id)
        );
    """)

        # Member skills (what each person actually does)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS member_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            skill_category TEXT,
            sub_skill TEXT,
            years_experience REAL,
            FOREIGN KEY (member_id) REFERENCES member(id)
        );
    """)

    # Member financial profile
    cur.execute("""
        CREATE TABLE IF NOT EXISTS member_financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            monthly_income REAL,
            monthly_expense REAL,
            credit_outstanding REAL,
            loan_repayment_rate REAL,
            savings REAL,
            last_updated TEXT,
            FOREIGN KEY (member_id) REFERENCES member(id)
        );
    """)

    # SHG production capacity
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shg_production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shg_id INTEGER,
            product_name TEXT,
            monthly_capacity REAL,
            supply_ready REAL,
            FOREIGN KEY (shg_id) REFERENCES shg(id)
        );
    """)

    # External demand centers
    cur.execute("""
        CREATE TABLE IF NOT EXISTS demand_centers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            district TEXT,
            state TEXT,
            product_required TEXT,
            quantity_required REAL,
            deadline TEXT,
            created_at TEXT
        );
    """)


    conn.commit()
    conn.close()