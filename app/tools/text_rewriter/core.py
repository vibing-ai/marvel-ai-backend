from typing import Optional, Dict, Any
from app.services.logger import setup_logger
from app.utils.document_loaders import get_docs
from app.api.error_utilities import LoaderError, ToolExecutorError
from .tools import TextRewriterPipeline, TextRewriterArgs

logger = setup_logger()

def validate_input(text: str, rewrite_style: str) -> None:
    """Validate input parameters"""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    if not rewrite_style or not rewrite_style.strip():
        raise ValueError("Invalid rewrite style")
    valid_styles = ["formal", "casual", "academic", "professional", "business_email", "summarize", "simplify"]
    if rewrite_style.lower() not in valid_styles:
        raise ValueError("Invalid rewrite style")

def executor(text: str,
             rewrite_style: str,
             file_url: Optional[str] = None,
             file_type: Optional[str] = None,
             lang: str = "en",
             verbose: bool = False,
             reading_level: Optional[str] = None,
             excluded_terms: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute text rewriting with enhanced error handling and validation.
    For the educator version, we support reading_level and excluded_terms.
    """
    try:
        # Validate inputs
        validate_input(text, rewrite_style)

        # Load document if file URL is provided
        docs = None
        if file_url and file_type:
            logger.info(f"Loading document from {file_url} of type {file_type}")
            try:
                docs = get_docs(file_url, file_type, True)
            except Exception as e:
                raise LoaderError(f"Failed to load document: {str(e)}")

        # Initialize arguments (only include advanced fields relevant for educators)
        text_rewriter_args = TextRewriterArgs(
            text=text,
            rewrite_style=rewrite_style,
            file_url=file_url,
            file_type=file_type,
            lang=lang,
            reading_level=reading_level,
            excluded_terms=excluded_terms
        )

        # Execute rewriting
        pipeline = TextRewriterPipeline(args=text_rewriter_args, verbose=verbose)
        output = pipeline.rewrite_text(docs)

        logger.info("Text rewriting completed successfully")
        return output

    except LoaderError as e:
        logger.error(f"Document loading error: {e}")
        raise ToolExecutorError(str(e))
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise ToolExecutorError(str(e))
    except Exception as e:
        error_message = f"Unexpected error in text rewriter: {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

