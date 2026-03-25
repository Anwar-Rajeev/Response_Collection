import streamlit as st
from utils.db import init_db, get_active_session, count_responses

st.set_page_config(
    page_title="PulseCloud Live",
    page_icon="☁️",
    layout="wide",
)

init_db()

st.markdown(
    """
    <style>
    .hero {
        padding: 2.2rem 2rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #101828 0%, #1d2939 45%, #344054 100%);
        color: white;
        box-shadow: 0 18px 50px rgba(16, 24, 40, 0.18);
        margin-bottom: 1rem;
    }
    .hero h1 { font-size: 3rem; margin-bottom: 0.2rem; }
    .hero p { font-size: 1.1rem; opacity: 0.92; }
    .tile {
        background: #ffffff;
        border: 1px solid #eaecf0;
        border-radius: 20px;
        padding: 1.2rem;
        box-shadow: 0 10px 30px rgba(16, 24, 40, 0.06);
        height: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

active = get_active_session()
response_count = count_responses(active["id"]) if active else 0

st.markdown(
    """
    <div class="hero">
        <h1>☁️ PulseCloud Live</h1>
        <p>Create live classroom word clouds, let students join by QR code, and watch opinions appear in real time.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="tile">
            <h3>📱 Student Response</h3>
            <p>Students open a phone-friendly screen and submit words or short opinions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
        <div class="tile">
            <h3>🎥 Live Word Cloud</h3>
            <p>Project the presenter view and watch the cloud update live as new responses arrive.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
        <div class="tile">
            <h3>⚙️ Admin Dashboard</h3>
            <p>Set the question, generate a QR code, clear responses, and reset the whole session.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

left, right = st.columns([1.15, 0.85])
with left:
    st.subheader("Current session")
    if active:
        st.success(f"Active question: {active['question']}")
        c1, c2 = st.columns(2)
        c1.metric("Session code", active["session_code"])
        c2.metric("Responses collected", response_count)
    else:
        st.info("No active session. Go to **Admin Dashboard** and start one.")

with right:
    st.subheader("Use the app")
    st.page_link("pages/1_Student_Response.py", label="Open Student Response", icon="📱")
    st.page_link("pages/2_Live_Word_Cloud.py", label="Open Live Word Cloud", icon="🎥")
    st.page_link("pages/3_Admin_Dashboard.py", label="Open Admin Dashboard", icon="⚙️")

st.caption("Tip: Deploy this on Streamlit Community Cloud, set your public app URL in the Admin page, and project the Live Word Cloud screen in class.")
