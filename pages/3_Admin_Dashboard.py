import streamlit as st

from utils.db import (
    clear_active_question,
    clear_all_data,
    clear_responses,
    close_active_session,
    count_responses,
    create_session,
    get_active_session,
    get_responses,
    init_db,
    update_active_question,
    update_public_url,
)
from utils.helpers import build_student_link, make_qr_code, responses_to_dataframe

st.set_page_config(page_title="Admin Dashboard | PulseCloud Live", page_icon="⚙️", layout="wide")
init_db()

ADMIN_PASSWORD = "mine123word"

st.markdown(
    """
    <style>
    .admin-banner {
        padding: 1.3rem 1.5rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #fdf2f8 0%, #f5f3ff 55%, #eef2ff 100%);
        border: 1px solid #e9d5ff;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

st.markdown("<div class='admin-banner'>", unsafe_allow_html=True)
st.title("⚙️ Admin Dashboard")
st.write("Create a live question, show the QR code, and manage the session in class.")
st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.admin_ok:
    pwd = st.text_input("Enter admin password", type="password")
    if st.button("Unlock dashboard"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_ok = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

active = get_active_session()

left, right = st.columns([1.25, 1])

with left:
    st.subheader("Create or update session")
    public_url = st.text_input(
        "Public app URL",
        value=active.get("public_url", "") if active else "",
        placeholder="https://your-app-name.streamlit.app",
        help="Paste your deployed Streamlit app URL here to generate the student QR code.",
    )

    if active:
        question_default = active["question"] or ""
    else:
        question_default = "What one word comes to your mind right now?"

    question = st.text_area(
        "Question",
        value=question_default,
        height=110,
        placeholder="Enter the live question you want students to answer...",
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Start new session", use_container_width=True):
            if not question.strip():
                st.error("Please enter a question before starting a session.")
            else:
                create_session(question, public_url)
                st.success("New live session started.")
                st.rerun()
    with c2:
        if st.button("💾 Update current question", use_container_width=True, disabled=not active):
            if active:
                update_active_question(question)
                if public_url.strip():
                    update_public_url(public_url)
                st.success("Active question updated.")
                st.rerun()

    st.subheader("Session controls")
    c3, c4, c5 = st.columns(3)
    with c3:
        if st.button("🧹 Clear responses", use_container_width=True, disabled=not active):
            clear_responses(active["id"])
            st.success("Responses cleared.")
            st.rerun()
    with c4:
        if st.button("❌ Clear question", use_container_width=True, disabled=not active):
            clear_active_question()
            st.success("Question cleared.")
            st.rerun()
    with c5:
        if st.button("🛑 Close session", use_container_width=True, disabled=not active):
            close_active_session()
            st.success("Session closed.")
            st.rerun()

    if st.button("🔥 Delete all sessions and responses", type="primary"):
        clear_all_data()
        st.success("Everything has been deleted.")
        st.rerun()

with right:
    st.subheader("Live session status")
    if active:
        total = count_responses(active["id"])
        st.success(f"Active session code: {active['session_code']}")
        st.write(f"**Question:** {active['question'] or '(blank)'}")
        st.write(f"**Responses:** {total}")

        if public_url.strip() and active:
            if active.get("public_url") != public_url.strip():
                update_public_url(public_url)
                active = get_active_session()
            student_link = build_student_link(active["public_url"], active["session_code"])
            qr_img = make_qr_code(student_link)
            st.image(qr_img, caption="Scan to join", use_container_width=True)
            st.code(student_link, language=None)
            st.page_link("pages/2_Live_Word_Cloud.py", label="Open presenter screen", icon="🎥")
        else:
            st.info("Enter your public app URL to create the QR code.")

        df = responses_to_dataframe(get_responses(active["id"]))
        if not df.empty:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download responses CSV",
                data=csv,
                file_name=f"pulsecloud_{active['session_code']}_responses.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.dataframe(df, use_container_width=True, height=260)
        else:
            st.caption("Responses will appear here.")
    else:
        st.info("No active session right now.")
