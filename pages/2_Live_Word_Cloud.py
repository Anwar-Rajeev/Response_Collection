import matplotlib.pyplot as plt
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils.db import count_responses, get_active_session, get_responses, init_db
from utils.helpers import build_student_link, make_qr_code, make_wordcloud_figure, recent_responses_dataframe, word_frequency

st.set_page_config(page_title="Live Word Cloud | PulseCloud Live", page_icon="🎥", layout="wide")
init_db()

st_autorefresh(interval=2000, key="pulsecloud_refresh")

st.markdown(
    """
    <style>
    .screen {
        padding: 1.2rem;
        border-radius: 28px;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #111827 100%);
        color: white;
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.22);
        margin-bottom: 1rem;
    }
    .question {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

active = get_active_session()

if not active:
    st.warning("No active session. Start one from the Admin Dashboard.")
    st.stop()

responses = get_responses(active["id"])
response_count = count_responses(active["id"])
freq = word_frequency(responses)

st.markdown("<div class='screen'>", unsafe_allow_html=True)
head1, head2 = st.columns([4.6, 1.4])
with head1:
    st.markdown("### ☁️ PulseCloud Live")
    st.markdown(f"<div class='question'>{active['question'] or 'Waiting for a question...'}</div>", unsafe_allow_html=True)
with head2:
    st.metric("Responses", response_count)
    st.metric("Unique words", len(freq))

left, right = st.columns([4.7, 1.3])
with left:
    fig = make_wordcloud_figure(responses)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with right:
    st.subheader("Join live")
    if active.get("public_url"):
        student_link = build_student_link(active["public_url"], active["session_code"])
        qr_img = make_qr_code(student_link)
        st.image(qr_img, caption="Scan to respond", use_container_width=True)
        st.code(student_link, language=None)
    else:
        st.info("Set your public app URL in Admin Dashboard to generate a QR code.")

    st.subheader("Latest responses")
    recent_df = recent_responses_dataframe(responses, limit=8)
    if recent_df.empty:
        st.caption("Responses will appear here live.")
    else:
        for _, row in recent_df.iterrows():
            st.markdown(f"- **{row['response_text']}**")

st.markdown("</div>", unsafe_allow_html=True)
