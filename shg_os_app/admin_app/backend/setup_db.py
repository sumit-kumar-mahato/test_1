import sqlite3

# Connect to database (or create it)
conn = sqlite3.connect('impactathon_phase2.db')
cur = conn.cursor()

# Enable Foreign Keys support
cur.execute("PRAGMA foreign_keys = ON;")

# ==========================================
# 1. PARENT TABLES (Must be created first)
# ==========================================

# Create SHG (Self Help Group) Table first
cur.execute("""
    CREATE TABLE IF NOT EXISTS shg (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        formed_date TEXT
    );
""")

# Create Member Table (Links to SHG)
cur.execute("""
    CREATE TABLE IF NOT EXISTS member (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shg_id INTEGER,
        name TEXT NOT NULL,
        age INTEGER,
        FOREIGN KEY (shg_id) REFERENCES shg(id)
    );
""")

# ==========================================
# 2. CHILD TABLES (Your code)
# ==========================================

# Member skills (References member)
cur.execute("""
    CREATE TABLE IF NOT EXISTS member_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        skill_category TEXT,    -- e.g. Tailoring, Food Processing
        sub_skill TEXT,         -- e.g. School uniforms, Pickle making
        years_experience REAL,
        FOREIGN KEY (member_id) REFERENCES member(id)
    );
""")

# Member financial profile (References member)
cur.execute("""
    CREATE TABLE IF NOT EXISTS member_financials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        monthly_income REAL,
        monthly_expense REAL,
        credit_outstanding REAL,
        loan_repayment_rate REAL,  -- percentage (0–1)
        savings REAL,
        last_updated TEXT,
        FOREIGN KEY (member_id) REFERENCES member(id)
    );
""")

# SHG production capacity (References shg)
cur.execute("""
    CREATE TABLE IF NOT EXISTS shg_production (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shg_id INTEGER,
        product_name TEXT,
        monthly_capacity REAL,   -- how much they can produce
        supply_ready REAL,       -- how much is realistically ready to deploy
        FOREIGN KEY (shg_id) REFERENCES shg(id)
    );
""")

# ==========================================
# 3. INDEPENDENT TABLES
# ==========================================

# Demand centers (No Foreign Keys, can be anywhere)
cur.execute("""
    CREATE TABLE IF NOT EXISTS demand_centers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,            -- e.g. "Ahmedabad city"
        district TEXT,
        state TEXT,
        product_required TEXT,    -- e.g. "paper bags"
        quantity_required REAL,
        deadline TEXT,
        created_at TEXT
    );
""")

# Save changes and close
conn.commit()
print("Tables created successfully in proper order.")
conn.close()