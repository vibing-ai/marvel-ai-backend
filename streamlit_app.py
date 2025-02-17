
import streamlit as st
from app.tools.text_rewriter.core import executor

st.set_page_config(
    page_title="Text Rewriter",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Streamlit to handle websocket connections
st.server.websocket_headers = {}
st.server.max_message_size = 200

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
                st.write(result.original)
                
                st.subheader(f"Rewritten Text ({style.title()} Style)")
                st.write(result.rewritten)
                
                st.subheader("Changes Made")
                st.write(result.changes_explained)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter some text to rewrite.")
