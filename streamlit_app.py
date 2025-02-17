
import streamlit as st
from app.tools.text_rewriter.core import executor

# Configure page settings at the very start
st.set_page_config(
    page_title="Text Rewriter",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Text Rewriter")

# Input text area
text = st.text_area("Enter text to rewrite:", "The cat sat on the mat. It was looking at a bird flying nearby.")

# Style selector
style = st.selectbox(
    "Choose writing style:",
    ["formal", "casual", "academic", "professional"]
)

# Submit button
if st.button("Rewrite Text"):
    try:
        result = executor(text=text, rewrite_style=style, lang="en")
        
        # Display results
        st.subheader("Original Text:")
        st.write(result.original)
        
        st.subheader(f"Rewritten Text ({style.title()} Style):")
        st.write(result.rewritten)
        
        st.subheader("Changes Made:")
        st.write(result.changes_explained)
    except Exception as e:
        st.error(f"Error: {str(e)}")
