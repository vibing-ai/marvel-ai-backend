from typing import Any, Dict, Optional
from app.api.error_utilities import FileHandlerError
from app.utils.document_loaders import get_docs
from app.tools.notes_generator.tools import NotesGeneratorPipeline
from app.services.logger import setup_logger

logger = setup_logger(__name__)

def executor(
    topic: str,
    page_layout: str,
    text: Optional[str] = None,
    text_file_url: Optional[str] = None,
    text_file_type: Optional[str] = None,
    lang: str = "en"
) -> Dict[str, str]:
    """
    Executor function for generating notes using a retrieval + generation pipeline.

    Args:
        text_file_url (str): URL for the document to load.
        text_file_type (str): The type of document (pdf, docx, csv, etc.).
        text (str): Plain text input if the user wants to pass text directly.
        topic (str): Focus or topic for the notes generation.
        lang (str): Language code (e.g. 'en', 'es', 'fr', etc.) to guide multilingual generation.

    Returns:
        Dict[str, str]: Contains the status and generated notes.
    """

    try:
    #     logger.info("Notes generation started...")

        # Validate that at least one of text_file_url or text is provided
        if not text_file_url and not text:
            raise ValueError("Either 'text_file_url' or 'text' must be provided.")

        # Validate that if text_file_url is provided, text_file_type must also be provided
        if text_file_url and not text_file_type:
            raise ValueError("If 'text_file_url' is provided, 'text_file_type' must also be provided.")

        # 1. Load documents from text_file_url if provided and text_file_type is supported
        docs = []
        if text_file_url and text_file_type:
            if not isinstance(text_file_type, str):
                raise ValueError("Unsupported text_file_type: must be a string.")
            logger.info("Notes generation started...")
            docs = get_docs(text_file_url, text_file_type, verbose=True)  # get_docs function from document_loaders.py

        # 2. If user gave raw text
        if text:
            text=text

        # 3. Run the pipeline with all input to generate notes
        pipeline = NotesGeneratorPipeline(
            topic=topic,
            page_layout=page_layout,
            text=text or "",
            text_file_url=text_file_url or "",
            text_file_type=text_file_type or "",
            lang=lang
        )
        notes = pipeline.generate_notes(docs)

        logger.info("Notes generation completed successfully.")
        return {"status": "success", "notes": notes}

    except ValueError as ve:
        logger.error(f"ValueError during notes generation: {str(ve)}")
        return {"status": "error", "message": str(ve)}
    except FileNotFoundError as fnf:
        logger.error(f"FileNotFoundError: {str(fnf)}")
        return {"status": "error", "message": "File not found. Please check the text_file_url or file path."}
    except Exception as e:
        logger.error(f"Unexpected error during notes generation: {str(e)}")
        return {"status": "error", "message": "An unexpected error occurred. Please try again."}