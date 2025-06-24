from typing import Any, Dict, Optional
from app.api.error_utilities import FileHandlerError
from app.utils.document_loaders import get_docs
from app.tools.text_rewriter.tools import TextRewriterPipeline
from app.services.logger import setup_logger

logger = setup_logger(__name__)

def executor(
    rewrite_instruction: str,
    text: Optional[str] = None,
    text_file_url: Optional[str] = None,
    text_file_type: Optional[Any] = None,
    lang: str = "en"
) -> Dict[str, str]:
    """
    Executor function for rewriting text using a generative pipeline based on user instructions.

    Args:
        rewrite_instruction (str): Instructions for how to rewrite the text (e.g. 'Simplify', 'Paraphrase', 'Translate to French').
        text (Optional[str]): Plain text input.
        text_file_url (Optional[str]): URL of the file to load (CSV, PDF, DOCX, PPT, TXT, etc.).
        text_file_type (Optional[Any]): Type of the document ('pdf', 'docx', 'txt', etc.).
        lang (str): Language code for output.

    Returns:
        Dict[str, str]: Contains 'status' and either 'rewritten_text' or 'message'.
    """
    try:
        # Validate inputs
        if not text_file_url and not text:
            raise ValueError("Either 'text_file_url' or 'text' must be provided.")
        if text_file_url and not text_file_type:
            raise ValueError("If 'text_file_url' is provided, 'text_file_type' must also be provided.")

        # Load documents if URL provided
        docs = []
        if text_file_url and text_file_type:
            if not isinstance(text_file_type, str):
                raise ValueError("Unsupported text_file_type: must be a string.")
            logger.info("Text rewriting started with document loading...")
            docs = get_docs(text_file_url, str(text_file_type), verbose=True)

        # Initialize pipeline and generate rewrite
        pipeline = TextRewriterPipeline(
            rewrite_instruction=rewrite_instruction,
            text=text or "",
            text_file_url=text_file_url or "",
            text_file_type=str(text_file_type) if text_file_type is not None else "",
            lang=lang
        )
        rewritten = pipeline.rewrite(docs)

        logger.info("Text rewriting completed successfully.")
        return {"status": "success", "rewritten_text": rewritten}

    except ValueError as ve:
        logger.error(f"ValueError during text rewriting: {str(ve)}")
        return {"status": "error", "message": str(ve)}
    except FileNotFoundError as fnf:
        logger.error(f"FileNotFoundError during text rewriting: {str(fnf)}")
        return {"status": "error", "message": "File not found. Please check the text_file_url or file path."}
    except Exception as e:
        logger.error(f"Unexpected error during text rewriting: {str(e)}")
        return {"status": "error", "message": "An unexpected error occurred. Please try again."}
