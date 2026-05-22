import streamlit as st
from reviewer import review_code, has_openai_key

st.set_page_config(page_title="AI Code Reviewer", page_icon="🧠", layout="wide")

page_style = """
<style>
body {
    background: #eef2ff;
}
.stApp {
    color: #0f172a;
}
.stApp .css-18e3th9 {
    background: #eef2ff;
}
.section-header {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
}
.card {
    background: #f8fbff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 14px 50px rgba(15, 23, 42, 0.08);
}
</style>
"""

st.markdown(page_style, unsafe_allow_html=True)

st.markdown("# AI Code Reviewer")
st.markdown("Paste code or upload a file to get a structured review with language, time complexity, space complexity, score, and optimized best version.")

with st.container():
    left, right = st.columns([2, 1])

    with left:
        uploaded_file = st.file_uploader("Upload source code", type=["py", "c", "cpp", "java", "js", "txt"])
        code_input = st.text_area("Paste code here", height=360)
        filename = None
        if uploaded_file is not None:
            filename = uploaded_file.name
            try:
                code_text = uploaded_file.read().decode("utf-8")
            except Exception:
                code_text = uploaded_file.read().decode("latin-1")
            if code_text:
                code_input = code_text

        analyze = st.button("Analyze Code")

    with right:
        st.markdown("## Review Output")
        st.info("The review will show only the required fields: language, time complexity, space complexity, score, and best version.")
        st.empty()

if analyze and code_input.strip():
    with st.spinner("Reviewing code..."):
        review = review_code(code_input, filename)

    st.markdown("## Code Review")
    st.markdown(f"**Language:** {review.get('language', 'Unknown')}")
    st.markdown(f"**Time Complexity:** {review.get('time_complexity', 'Unknown')}")
    st.markdown(f"**Space Complexity:** {review.get('space_complexity', 'Unknown')}")
    st.markdown(f"**Score:** {review.get('score', 'N/A')}")

    st.markdown("### Best Version")
    st.code(review.get("best_version", ""), language=review.get("language", "python").lower())

elif analyze:
    st.error("Please provide code by pasting it or uploading a source file.")

st.markdown("---")
st.markdown("Designed for clean and professional code review in a simple, no-database Python and Streamlit app.")
