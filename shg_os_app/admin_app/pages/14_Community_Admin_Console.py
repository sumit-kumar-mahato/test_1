import sys, os
import streamlit as st

# ========================
# PATH SETUP
# ========================
PHASE2_ROOT = r"C:\Users\sumit\Desktop\IMPACTATHON\PHASE_2"
ADMIN_BACKEND = os.path.join(PHASE2_ROOT, "streamlit_app", "backend")
sys.path.insert(0, ADMIN_BACKEND)

from backend.database import get_connection
from chat_backend import save_message, load_messages


# ========================
# STREAMLIT PAGE CONFIG
# ========================
st.set_page_config(
    page_title="Community Admin Console",
    page_icon="📢",
    layout="wide",
)

st.title("📢 Community Admin Console")
st.caption("Adani Foundation can publish announcements, success stories and view all community messages.")



# ============================================================
# 1. ADMIN MESSAGE / ANNOUNCEMENT COMPOSER
# ============================================================
st.markdown("### ✍️ Post Announcement / Success Story")

col1, col2 = st.columns([2, 1])

with col1:
    announcement_text = st.text_area(
        "Write your message:",
        placeholder="Example: Prerna SHG from Jamshedpur completed a bulk order of 10,000 eco-friendly bags...",
        height=150,
    )

with col2:
    conn = get_connection()
    shg_list = conn.execute(
        "SELECT id, name, village, district FROM shg ORDER BY name"
    ).fetchall()
    conn.close()

    scope = st.radio("Target audience:", ["All SHGs (Global)", "Specific SHG"], index=0)

    target_shg_id = None
    if scope == "Specific SHG":
        options = {
            f"{r[1]} ({r[2]}, {r[3]}) [ID {r[0]}]": r[0]
            for r in shg_list
        }
        selected = st.selectbox("Choose SHG", list(options.keys()))
        target_shg_id = options[selected]

    uploaded_file = st.file_uploader(
        "Attach media (optional)",
        type=["jpg", "jpeg", "png", "mp4", "mov", "pdf", "docx"],
    )


if st.button("📤 Publish to Community", use_container_width=True):
    if not announcement_text.strip() and not uploaded_file:
        st.error("Please write something or attach a file.")
    else:
        save_message(
            user_id=None,
            shg_id=target_shg_id,
            message=announcement_text.strip(),
            uploaded_file=uploaded_file,
            is_admin=1,
        )
        st.success("Announcement successfully published!")



# ============================================================
# 2. COMMUNITY FEED VIEW (for Admin)
# ============================================================
st.markdown("---")
st.markdown("### 📡 Live Community Feed")

# Filter options
filter_mode = st.radio(
    "View",
    ["All messages", "Announcements only", "By SHG"],
    horizontal=True,
)

filter_shg_id = None
if filter_mode == "By SHG":
    conn = get_connection()
    shg_list = conn.execute(
        "SELECT id, name, village, district FROM shg ORDER BY name"
    ).fetchall()
    conn.close()

    options = {
        f"{r[1]} ({r[2]}, {r[3]}) [ID {r[0]}]": r[0]
        for r in shg_list
    }
    selected = st.selectbox("Filter by SHG", list(options.keys()))
    filter_shg_id = options[selected]

# Search bar
search_text = st.text_input("Search messages")

# Load filtered messages
if filter_mode == "All messages":
    rows = load_messages(filter_mode="all", search_text=search_text)

elif filter_mode == "Announcements only":
    rows = load_messages(filter_mode="announcements", search_text=search_text)

else:
    rows = load_messages(
        filter_mode="my_shg",
        my_shg_id=filter_shg_id,
        search_text=search_text,
    )


# ============================================================
# Chat Bubble HTML / CSS
# ============================================================
st.markdown("""
<style>
.chat-container {
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 12px;
    background: #020617;
    max-height: 600px;
    overflow-y: auto;
}

.bubble-admin {
    background: #8E44AD;
    color: white;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 10px 0;
    max-width: 85%;
    font-size: 15px;
}

.bubble-user {
    background: #1F2937;
    color: white;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 10px 0;
    max-width: 85%;
    font-size: 15px;
}

.meta-line {
    font-size: 11px;
    color: #C5C5C5;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)


# Chat Feed Container
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)


# ============================================================
# RENDER MESSAGES
# ============================================================
for row in rows:
    msg_id, user_id, shg_id, message, media_path, media_type, is_admin, ts = row

    # Get SHG name for header
    conn = get_connection()
    if shg_id:
        s = conn.execute(
            "SELECT name, village, district, state FROM shg WHERE id = ?",
            (shg_id,)
        ).fetchone()
    else:
        s = None
    conn.close()

    if s:
        shg_label = f"{s[0]} ({s[1]}, {s[2]}, {s[3]})"
    else:
        shg_label = "All SHGs"

    # Bubble rendering
    if is_admin:
        st.markdown(
            f"""
            <div class='bubble-admin'>
                <div class='meta-line'>📢 Admin • {shg_label} • {ts}</div>
                {message or ""}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class='bubble-user'>
                <div class='meta-line'>👥 SHG ID {shg_id} • {ts}</div>
                {message or ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Media preview
    if media_path:
        if media_type == "image":
            st.image(media_path, width=350)
        elif media_type == "video":
            st.video(media_path)
        else:
            st.write(f"📎 Attached file: `{os.path.basename(media_path)}`")

st.markdown("</div>", unsafe_allow_html=True)

