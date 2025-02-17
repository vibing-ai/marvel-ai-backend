
import streamlit as st
from app.tools.text_rewriter.core import executor

# Configure page settings
st.set_page_config(
    page_title="Text Rewriter",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title of the application
st.title("Text Rewriter")

# Input text area
text = st.text_area("Enter text to rewrite:", "The cat sat on the mat. It was looking at a bird flying nearby.", height=150)

# Style selector
style = st.selectbox(
    "Choose writing style:",
    ["formal", "casual", "academic", "professional"]
)

# Submit button
if st.button("Rewrite Text"):
    if text.strip():
        with st.spinner('Rewriting text...'):
            try:
                result = executor(text=text, rewrite_style=style, lang="en")

                # Original text
                st.subheader("Original Text")
                st.write(text)

                # Rewritten text
                st.subheader(f"Rewritten Text ({style.title()} Style)")
                if isinstance(result, dict):
                    st.write(result.get('rewritten', 'No rewritten text available'))
                    if 'changes_explained' in result:
                        st.subheader("Changes Made")
                        st.write(result['changes_explained'])
                else:
                    st.write(result.rewritten if hasattr(result, 'rewritten') else 'No rewritten text available')
                    if hasattr(result, 'changes_explained'):
                        st.subheader("Changes Made")
                        st.write(result.changes_explained)

            except Exception as e:
                st.error(f"Error during text rewriting: {str(e)}")
    else:
        st.warning("Please enter some text to rewrite.")
