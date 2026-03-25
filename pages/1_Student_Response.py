import streamlit as st
from utils.db import add_response, get_active_session, init_db

st.set_page_config(page_title="Student Response | PulseCloud Live", page_icon="📱", layout="centered")
init_db()

st.markdown(
    """
    <style>
    .student-card {
        padding: 1.5rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #ecfeff 0%, #f5f3ff 50%, #eff6ff 100%);
        border: 1px solid #dbeafe;
        box-shadow: 0 14px 40px rgba(2, 132, 199, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

active = get_active_session()
session_param = st.query_params.get("session", "")

st.markdown("<div class='student-card'>", unsafe_allow_html=True)
st.title("📱 Student Response")

if not active:
    st.warning("There is no active question right now.")
    st.stop()

if session_param and session_param != active["session_code"]:
    st.error("This session link is no longer active. Ask your teacher to show the latest QR code.")
    st.stop()

question = active["question"] or "A new question will appear soon."
st.markdown(f"### {question}")
st.caption(f"Session code: {active['session_code']}")

with st.form("student_form", clear_on_submit=True):
    response = st.text_input(
        "Your response",
        placeholder="Type one word or a short phrase...",
        max_chars=80,
    )
    submit = st.form_submit_button("Submit response")

if submit:
    try:
        add_response(active["id"], response)
        st.success("Response submitted. Watch the live screen for your word to appear.")
        st.balloons()
    except ValueError as exc:
        st.error(str(exc))

st.info("Keep your response short. One word or a very short phrase works best for word clouds.")
st.markdown("</div>", unsafe_allow_html=True)
