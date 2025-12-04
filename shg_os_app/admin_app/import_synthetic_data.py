import pandas as pd
import sqlite3
from faker import Faker
from datetime import datetime
import random

DB_PATH = "shg_os.db"
fake = Faker("en_IN")

# -----------------------
# Load CSVs
# -----------------------
members = pd.read_csv("members.csv")
skills = pd.read_csv("skills.csv")
financials = pd.read_csv("financials.csv")
products = pd.read_csv("products.csv")
capacity = pd.read_csv("capacity.csv")

N = len(members)  # 1000 members
SHG_COUNT = 100
MEMBERS_PER_SHG = 10

# -----------------------
# Smart SHG Names
# -----------------------
CLUSTERS = {
    "Tailoring": ["Uday Tailoring SHG", "Sakhi Silai SHG", "Lakshmi Tailor SHG"],
    "Papad Making": ["Pragati Papad SHG", "Ujjwal Papad SHG"],
    "Pickle Making": ["Annapurna Pickle SHG", "Shakti Pickle SHG"],
    "Pottery": ["Mitti Kala SHG", "Matira Pottery SHG"],
    "Bag Stitching": ["Vastra Bags SHG", "EcoBag SHG"],
    "Goat Rearing": ["Vatsalya Goat SHG", "Pashu Samvardhan SHG"],
    "Dairy Farming": ["Gokul Dairy SHG", "Amrit Dairy SHG"],
    "Spice Grinding": ["Masala Udyog SHG", "Swad Masala SHG"],
    "Handicraft": ["Kalakruti Craft SHG", "Samriddhi Craft SHG"],
    "Beautician": ["Roopkala Beauty SHG", "Sundaram SHG"]
}

STATES = ["Gujarat", "Rajasthan", "Maharashtra", "Madhya Pradesh"]
DISTRICTS = ["Kutch", "Vadodara", "Ahmedabad", "Surat", "Udaipur", "Nagpur", "Indore"]
VILLAGES = ["Rampur", "Madhavpura", "Dharpur", "Khadki", "Bhimpur", "Dharmaj", "Anandpura"]

# -----------------------
# Step 1 — Build 100 SHGs
# -----------------------
shg_rows = []
shg_skill_map = {}  # SHG ID → Skill Category

for shg_id in range(1, SHG_COUNT+1):
    skill_type = random.choice(list(CLUSTERS.keys()))
    shg_skill_map[shg_id] = skill_type

    name = random.choice(CLUSTERS[skill_type])
    village = random.choice(VILLAGES)
    district = random.choice(DISTRICTS)
    state = random.choice(STATES)

    shg_rows.append([shg_id, name, village, district, state, datetime.now().isoformat()])

shg_df = pd.DataFrame(
    shg_rows,
    columns=["id", "name", "village", "district", "state", "created_at"]
)

# -----------------------
# DB Connection
# -----------------------
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Insert SHGs
for _, r in shg_df.iterrows():
    cur.execute(
        "INSERT INTO shg (id, name, village, district, state, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (int(r.id), r.name, r.village, r.district, r.state, r.created_at),
    )

# -----------------------
# Step 2 — Insert Members & Attributes
# -----------------------
start = 0

for shg_id in range(1, SHG_COUNT + 1):
    batch = members.iloc[start:start + MEMBERS_PER_SHG]
    start += MEMBERS_PER_SHG

    for _, m in batch.iterrows():
        member_id = int(m.member_id)

        # Insert member
        cur.execute(
            """INSERT INTO member (id, shg_id, name, phone, role, joined_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                member_id,
                shg_id,
                m.name,
                fake.phone_number(),
                "member",
                datetime.now().isoformat(),
            )
        )

        # Insert skill
        ms = skills[skills.member_id == member_id].iloc[0]
        cur.execute(
            """INSERT INTO member_skills
               (member_id, skill_category, sub_skill, years_experience)
               VALUES (?, ?, ?, ?)""",
            (member_id, ms.skill_category, ms.sub_skill, float(ms.years_experience))
        )

        # Insert financial data
        fs = financials[financials.member_id == member_id].iloc[0]
        cur.execute(
            """INSERT INTO member_financials
               (member_id, monthly_income, monthly_expense, credit_outstanding,
                loan_repayment_rate, savings, last_updated)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                member_id,
                float(fs.monthly_income),
                float(fs.monthly_expense),
                float(fs.credit_outstanding),
                float(fs.loan_repayment_rate),
                float(fs.savings),
                datetime.now().isoformat(),
            )
        )

        # Insert product
        ps = products[products.member_id == member_id].iloc[0]
        cur.execute(
            """INSERT INTO product
               (shg_id, name, category, unit, cost_price, selling_price, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                shg_id,
                ps.product_name,
                ps.category,
                "unit",
                ps.unit_price,
                ps.unit_price * 1.4,
                datetime.now().isoformat(),
            )
        )

        # Insert production capacity
        cs = capacity[capacity.member_id == member_id].iloc[0]
        cur.execute(
            """INSERT INTO shg_production
               (shg_id, product_name, monthly_capacity, supply_ready)
               VALUES (?, ?, ?, ?)""",
            (
                shg_id,
                ps.product_name,
                float(cs.monthly_capacity),
                float(cs.supply_ready),
            )
        )

conn.commit()
conn.close()

print("🎉 Synthetic data imported successfully into SHG OS database!")
