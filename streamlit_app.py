
import streamlit as st
from app.tools.text_rewriter.core import executor

st.set_page_config(
    page_title="Text Rewriter",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Text Rewriter")

text = st.text_area("Enter text to rewrite:", "The cat sat on the mat. It was looking at a bird flying nearby.", height=150)

style = st.selectbox(
    "Choose writing style:",
    ["formal", "casual", "academic", "professional"]
)

if st.button("Rewrite Text"):
    if text.strip():
        with st.spinner('Rewriting text...'):
            try:
                result = executor(text=text, rewrite_style=style, lang="en")
                
                st.subheader("Original Text")
                st.info(result.original)
                
                st.subheader(f"Rewritten Text ({style.title()} Style)")
                st.write("Rewritten version:", result.rewritten)
                
                st.subheader("Changes Made")
                for change in result.changes_explained.split('\n'):
                    if change.strip():
                        st.write("•", change.strip())
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter some text to rewrite.")
