from typing import Optional, List
from app.utils.document_loaders import get_docs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError, FileHandlerError
from app.tools.notes_generator.tools import NotesGeneratorPipeline
from app.services.schemas import NotesGeneratorArgs

logger = setup_logger()

def executor(input_text: str,
             focus: str,
             file_url: Optional[str] = None,
             file_type: Optional[str] = None,
             lang: str = "en",
             verbose: bool = False) -> dict:
    """
    Executes the Notes Generator Pipeline.

    Args:
        input_text (str): The primary content to generate notes from.
        focus (str): The main topic or focus area for the notes.
        file_url (Optional[str], default=None): URL of the document to process, if applicable.
        file_type (Optional[str], default=None): The type of file being processed (CSV, PDF, DOCX, etc.).
        lang (str, default="en"): The language of the generated notes.
        verbose (bool, default=False): Flag to enable detailed logging.

    Returns:
        dict: A structured dictionary containing the generated notes.

    Raises:
        ToolExecutorError: If there's an issue during the execution of the pipeline.
        ValueError: If an unexpected error occurs.
    """

    try:
        if not input_text.strip():
            raise ValueError("Input text cannot be empty.")

        if file_type:
            logger.info(f"Loading document from {file_url}")

        # Load document if file_url and file_type are provided
        docs: Optional[List[str]] = None
        if file_url and file_type:
            docs = get_docs(file_url, file_type, True)

        # Create argument object for the Notes Generator
        notes_generator_args = NotesGeneratorArgs(
            input_text=input_text,
            focus=focus,
            file_url=file_url,
            file_type=file_type,
            lang=lang,
        )

        # Initialize and execute the Notes Generator Pipeline
        output = NotesGeneratorPipeline(
            args=notes_generator_args,
            verbose=verbose
        ).generate_notes_executor(docs)

        logger.info("Notes generation completed successfully")
        return output

    except LoaderError as e:
        error_message = f"Error in Notes Generator Pipeline -> {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except FileHandlerError as e:
        error_message = f"Document loading failed: {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Unexpected error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
