from datetime import datetime
from .database import get_connection

# --------- Skills ----------

def add_skill(member_id, skill_category, sub_skill, years_experience):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO member_skills (member_id, skill_category, sub_skill, years_experience)
        VALUES (?, ?, ?, ?)
        """,
        (member_id, skill_category, sub_skill, years_experience),
    )
    conn.commit()
    conn.close()

def get_skills_for_member(member_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT skill_category, sub_skill, years_experience
        FROM member_skills
        WHERE member_id = ?
        """,
        (member_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_skilled_members():
    """
    Returns list of (member_id, skill_category, sub_skill, years_experience)
    across all SHGs – useful for clustering.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT member_id, skill_category, sub_skill, years_experience
        FROM member_skills
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows

# --------- Financials ----------

def upsert_member_financials(
    member_id,
    monthly_income,
    monthly_expense,
    credit_outstanding,
    loan_repayment_rate,
    savings,
):
    conn = get_connection()
    cur = conn.cursor()

    # Check if exists
    cur.execute(
        "SELECT id FROM member_financials WHERE member_id = ?",
        (member_id,),
    )
    row = cur.fetchone()

    if row:
        cur.execute(
            """
            UPDATE member_financials
            SET monthly_income = ?, monthly_expense = ?, credit_outstanding = ?,
                loan_repayment_rate = ?, savings = ?, last_updated = ?
            WHERE member_id = ?
            """,
            (
                monthly_income,
                monthly_expense,
                credit_outstanding,
                loan_repayment_rate,
                savings,
                datetime.now().isoformat(),
                member_id,
            ),
        )
    else:
        cur.execute(
            """
            INSERT INTO member_financials (
                member_id, monthly_income, monthly_expense,
                credit_outstanding, loan_repayment_rate, savings, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                member_id,
                monthly_income,
                monthly_expense,
                credit_outstanding,
                loan_repayment_rate,
                savings,
                datetime.now().isoformat(),
            ),
        )

    conn.commit()
    conn.close()

def get_financials_for_member(member_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT monthly_income, monthly_expense, credit_outstanding,
               loan_repayment_rate, savings
        FROM member_financials
        WHERE member_id = ?
        """,
        (member_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row
