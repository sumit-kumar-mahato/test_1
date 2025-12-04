import sys, os
import streamlit as st
from datetime import datetime

# Attach backend paths
PHASE2_ROOT = r"C:\Users\sumit\Desktop\IMPACTATHON\PHASE_2"
ADMIN_BACKEND = os.path.join(PHASE2_ROOT, "streamlit_app", "backend")
USER_BACKEND = os.path.join(PHASE2_ROOT, "user_app", "user_backend")

sys.path.insert(0, ADMIN_BACKEND)
sys.path.insert(0, USER_BACKEND)

from chat_backend import load_messages, save_message

st.set_page_config(page_title="SHG Community Chat", layout="wide")

if "logged_in" not in st.session_state:
    st.switch_page("pages/1_User_Login.py")

user = st.session_state["user"]

st.title("💬 SHG Community Chat")
st.caption("A vibrant space where SHG members ask for help, share updates, and celebrate achievements.")

# ---------------------------------------
# Message Feed Container
# ---------------------------------------
st.markdown("""
<style>
.chat-box {
    background-color: #0E1117;
    padding: 20px;
    height: 500px;
    overflow-y: scroll;
    border-radius: 12px;
    border: 1px solid #333;
}
.my-msg {
    background-color: #075E54;
    padding: 10px 15px;
    border-radius: 12px;
    color: white;
    max-width: 60%;
    margin-left: auto;
    margin-top: 8px;
}
.other-msg {
    background-color: #202C33;
    padding: 10px 15px;
    border-radius: 12px;
    color: white;
    max-width: 60%;
    margin-right: auto;
    margin-top: 8px;
}
.admin-msg {
    background-color: #8E44AD;
    padding: 12px 18px;
    border-radius: 12px;
    color: white;
    max-width: 70%;
    margin: 10px auto;
    text-align: center;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.subheader("📡 Live Community Feed")
chat_box = st.container()

messages = load_messages()

with chat_box:
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

    for row in messages:
        msg_id, user_id, shg_id, msg_text, media_path, media_type, is_admin, ts = row

        # ADMIN POST
        if is_admin == 1:
            st.markdown(f"""
                <div class='admin-msg'>
                    📢 ADMIN NOTICE<br>{msg_text}<br>
                    <span style='font-size:12px;'>{ts}</span>
                </div>
            """, unsafe_allow_html=True)
            continue

        # MESSAGE FROM SELF
        if user_id == user["id"]:
            bubble = "my-msg"
        else:
            bubble = "other-msg"

        st.markdown(f"<div class='{bubble}'>{msg_text}</div>", unsafe_allow_html=True)

        # Render media
        if media_path:
            if media_type == "image":
                st.image(media_path, width=250)
            elif media_type == "video":
                st.video(media_path)
            else:
                st.download_button("📎 Download File", media_path, os.path.basename(media_path))

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("✍️ Send a message")

msg = st.text_input("Your message")

uploaded_file = st.file_uploader(
    "Attach Image / Video / File", 
    type=["jpg", "jpeg", "png", "mp4", "mov", "pdf", "docx"]
)

if st.button("Send"):
    if msg.strip() == "" and uploaded_file is None:
        st.warning("Please type a message or upload a file.")
    else:
        save_message(
            user_id=user["id"],
            shg_id=user["shg_id"],
            message=msg.strip(),
            uploaded_file=uploaded_file,
            is_admin=0
        )
        st.success("Message sent!")

        st.rerun()
