import streamlit as st
from app.tools.text_rewriter.core import executor

st.set_page_config(
    page_title="Text Rewriter",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Text Rewriter")

text = st.text_area(
    label="Enter text to rewrite:",
    value="The cat sat on the mat. It was looking at a bird flying nearby.",
    height=150
)

style = st.selectbox(
    "Choose writing style:",
    ["formal", "casual", "academic", "professional"]
)

if st.button("Rewrite Text"):
    if text.strip():
        with st.spinner('Rewriting text...'):
            try:
                result = executor(text=text, rewrite_style=style, lang="en")

                # Clean up the "Rewritten version:" label if the model includes it
                rewritten_clean = result.rewritten.replace("Rewritten version:", "").strip()

                # If the line is still empty, show a fallback message
                if not rewritten_clean:
                    rewritten_clean = "No rewritten text was provided."

                st.subheader("Original Text")
                st.info(result.original)

                st.subheader(f"Rewritten Text ({style.title()} Style)")
                st.write(rewritten_clean)

                st.subheader("Changes Made")
                # The model's bullet points typically appear in changes_explained
                for change in result.changes_explained.split('\n'):
                    if change.strip():
                        st.write("•", change.strip())

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter some text to rewrite.")
