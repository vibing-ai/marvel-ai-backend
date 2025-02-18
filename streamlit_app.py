import streamlit as st
from app.tools.text_rewriter.core import executor
from app.api.error_utilities import ToolExecutorError

st.set_page_config(
    page_title="Text Rewriter",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Text Rewriter for Educators")

# Optionally select a file type or "None"
file_type = st.selectbox("Select File Type (Optional)", ["None", "pdf", "docx", "txt", "ppt", "csv"])

uploaded_file = st.file_uploader("Upload File to Rewrite (optional)", type=["pdf", "docx", "txt", "ppt", "csv"])

# Use text area if no file is uploaded
if file_type == "None" or uploaded_file is None:
    text = st.text_area("Original Text", value="", height=150)
else:
    text = ""

# Rewrite style dropdown
style = st.selectbox("Rewrite Style / Instructions", ["formal", "casual", "academic", "professional", "business_email", "summarize", "simplify"])

# Language selection
lang = st.selectbox("Language", ["en", "es", "fr", "de", "other"])

# Advanced Options for Educators (only reading_level and excluded_terms)
with st.expander("Advanced Options (Optional)"):
    reading_level = st.selectbox("Reading Level", ["None", "Elementary", "Middle School", "High School", "College"], index=0)
    excluded_terms = st.text_area("Excluded Terms (comma-separated)", help="Words or phrases you want to remain unchanged.")

if st.button("Rewrite Text"):
    final_text = ""
    # If a file is uploaded, you would parse it; otherwise, use the text area.
    if file_type != "None" and uploaded_file is not None:
        try:
            from app.utils.document_loaders import get_docs
            docs = get_docs(uploaded_file, file_type, True)
            if not docs or not docs[0].page_content.strip():
                st.warning("No text extracted from the file.")
            else:
                final_text = docs[0].page_content.strip()
        except Exception as e:
            st.error(f"Error parsing file: {e}")
    else:
        final_text = text

    if not final_text.strip():
        st.warning("No text found to rewrite. Please upload a file or enter text.")
    else:
        with st.spinner("Rewriting text..."):
            try:
                result = executor(
                    text=final_text,
                    rewrite_style=style,
                    file_url=None,   # we're handling the file ourselves
                    file_type=None,
                    lang=lang,
                    verbose=False,
                    reading_level=None if reading_level == "None" else reading_level,
                    excluded_terms=excluded_terms if excluded_terms.strip() else None
                )
                st.subheader("Original Text")
                st.info(result.original)
                st.subheader(f"Rewritten Text ({style.title()} Style)")
                st.write(result.rewritten)
                st.subheader("Changes Explained")
                for change in result.changes_explained.split('\n'):
                    if change.strip():
                        st.write("•", change.strip())
            except ToolExecutorError as te:
                st.error(f"Tool Error: {te}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
