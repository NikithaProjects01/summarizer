import json

import streamlit as st

from content_summarizer.summarizer import build_summary_response


st.set_page_config(page_title="Content Summarizer", page_icon="📝", layout="centered")

st.title("Content Summarizer")
st.write("Paste text or upload a text file, then generate a concise summary.")

uploaded_file = st.file_uploader(
    "Upload a text file",
    type=[
        "txt",
        "md",
        "csv",
        "log",
        "json",
        "xml",
        "html",
        "py",
        "js",
        "css",
        "yaml",
        "yml",
    ],
)

uploaded_text = ""
if uploaded_file is not None:
    uploaded_text = uploaded_file.getvalue().decode("utf-8", errors="replace")

text = st.text_area(
    "Text to summarize",
    value=uploaded_text,
    height=220,
    placeholder="Enter or paste your content here...",
)

col1, col2 = st.columns(2)
with col1:
    length = st.selectbox("Summary length", ["short", "medium", "detailed"], index=1)
with col2:
    style = st.selectbox("Output style", ["paragraph", "bullet points"], index=0)

if st.button("Generate Summary", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("Please enter text or upload a file.")
        st.stop()

    result = build_summary_response(text, length=length, style=style)

    st.subheader(result["title"])

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Main topic", result["main_topic"])
    metric2.metric("Sentiment", result["sentiment"])
    metric3.metric(
        "Reading time",
        f'{result["reading_time"]["summary"]}',
        delta=f'from {result["reading_time"]["original"]}',
        delta_color="inverse",
    )

    st.subheader("Summary")
    if style == "bullet points":
        for sentence in result["summary"].split(". "):
            sentence = sentence.strip()
            if sentence:
                st.write(f"- {sentence}{'' if sentence.endswith('.') else '.'}")
    else:
        st.write(result["summary"])

    st.subheader("Key Points")
    for point in result["key_points"]:
        st.write(f"- {point}")

    st.subheader("Keywords")
    st.write(", ".join(result["keywords"]))

    json_result = json.dumps(result, indent=2)
    st.download_button(
        "Download JSON",
        data=json_result,
        file_name="summary.json",
        mime="application/json",
    )
    st.download_button(
        "Download TXT",
        data=result["summary"],
        file_name="summary.txt",
        mime="text/plain",
    )
