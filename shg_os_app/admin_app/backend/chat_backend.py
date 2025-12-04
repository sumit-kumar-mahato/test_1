import os
import sqlite3
from datetime import datetime
from pathlib import Path
import uuid
import shutil

# ---------- PATHS ----------
PHASE2_ROOT = r"C:\Users\sumit\Desktop\IMPACTATHON\PHASE_2"
DB_PATH = Path(PHASE2_ROOT) / "streamlit_app" / "shg_os.db"
MEDIA_FOLDER = Path(PHASE2_ROOT) / "streamlit_app" / "uploads"

MEDIA_FOLDER.mkdir(parents=True, exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


# ---------- MEDIA HANDLING ----------
def save_media_file(uploaded_file):
    """
    Save an uploaded file (image / video / pdf / docx) into uploads folder
    and return (path, media_type).
    """
    ext = uploaded_file.name.split(".")[-1].lower()
    new_name = f"{uuid.uuid4()}.{ext}"
    save_path = MEDIA_FOLDER / new_name

    with open(save_path, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)

    if ext in ["jpg", "jpeg", "png", "gif"]:
        m_type = "image"
    elif ext in ["mp4", "mov", "avi", "mkv"]:
        m_type = "video"
    else:
        m_type = "file"

    return str(save_path), m_type


# ---------- SAVE MESSAGE ----------
def save_message(user_id: int | None,
                 shg_id: int | None,
                 message: str,
                 uploaded_file=None,
                 is_admin: int = 0):
    """
    Save a chat/community message.
    - user_id can be None/0 for admin system messages
    - shg_id can be None/0 for global messages
    - is_admin = 1 marks announcement/success post
    """
    conn = get_connection()
    cur = conn.cursor()

    media_path = None
    media_type = None

    if uploaded_file is not None:
        media_path, media_type = save_media_file(uploaded_file)

    ts = datetime.now().isoformat(timespec="seconds")

    cur.execute(
        """
        INSERT INTO community_chat
        (user_id, shg_id, message, media_path, media_type, is_admin, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, shg_id, message, media_path, media_type, is_admin, ts),
    )

    conn.commit()
    conn.close()


# ---------- LOAD MESSAGES ----------
def load_messages(filter_mode: str = "all",
                  my_shg_id: int | None = None,
                  search_text: str = ""):
    """
    Load messages with optional filters:

    filter_mode:
        - "all"
        - "my_shg"
        - "announcements"
    my_shg_id:
        used when filter_mode="my_shg"
    search_text:
        simple case-insensitive search in message text
    """
    conn = get_connection()
    cur = conn.cursor()

    base = "SELECT * FROM community_chat"
    where_clauses = []
    params: list = []

    if filter_mode == "my_shg" and my_shg_id is not None:
        where_clauses.append("(shg_id = ? OR is_admin = 1)")
        params.append(my_shg_id)
    elif filter_mode == "announcements":
        where_clauses.append("is_admin = 1")

    if search_text.strip():
        where_clauses.append("LOWER(message) LIKE ?")
        params.append(f"%{search_text.lower()}%")

    if where_clauses:
        base += " WHERE " + " AND ".join(where_clauses)

    base += " ORDER BY datetime(timestamp) ASC"

    cur.execute(base, params)
    rows = cur.fetchall()
    conn.close()
    return rows
