from collections import Counter
from io import BytesIO
from urllib.parse import quote

import matplotlib.pyplot as plt
import pandas as pd
import qrcode
import io
from wordcloud import STOPWORDS, WordCloud


CUSTOM_STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "your", "from", "have",
    "about", "into", "what", "when", "where", "which", "will", "they",
    "their", "been", "were", "would", "could", "should", "very",
}


def make_qr_code(data: str):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    if hasattr(img, "get_image"):
        img = img.get_image()

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def build_student_link(base_url: str, session_code: str) -> str:
    clean = base_url.rstrip("/")
    return f"{clean}/Student_Response?session={quote(session_code)}"


def responses_to_dataframe(responses):
    if not responses:
        return pd.DataFrame(columns=["response_text", "submitted_at"])
    return pd.DataFrame(responses)[["response_text", "submitted_at"]]


def recent_responses_dataframe(responses, limit=10):
    df = responses_to_dataframe(responses)
    return df.head(limit)


def word_frequency(responses):
    words = []
    for item in responses:
        words.extend(item["normalized_text"].split())
    filtered = [w for w in words if w and w not in STOPWORDS and w not in CUSTOM_STOPWORDS]
    return Counter(filtered)


def make_wordcloud_figure(responses, width=1400, height=700):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_axis_off()

    if not responses:
        ax.text(
            0.5,
            0.5,
            "No responses yet",
            ha="center",
            va="center",
            fontsize=28,
            weight="bold",
            transform=ax.transAxes,
        )
        return fig

    text_blob = " ".join(item["normalized_text"] for item in responses)
    wc = WordCloud(
        width=width,
        height=height,
        background_color="white",
        collocations=False,
        min_font_size=12,
        max_words=150,
        prefer_horizontal=0.9,
    ).generate(text_blob)

    ax.imshow(wc, interpolation="bilinear")
    return fig


def fig_to_png_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf
