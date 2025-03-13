from app.utils.document_loaders import get_docs
from app.tools.outline_generator import executor as outline_executor
from app.tools.slides_generator import executor as slides_executor
from app.services.schemas import PresentationGeneratorArgs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(instructionalLevel: str,
             slideCount: int,
             text: str,
             objectives: str = "",
             additional_comments: str = "",
             objectives_file_url: str = "",
             objectives_file_type: str = "",
             additional_comments_file_url: str = "",
             additional_comments_file_type: str = "",
             verbose: bool = False):
    """
    Execute the presentation generation process (outline only for this context).

    Args:
        instructionalLevel (str): The educational level (e.g., Elementary, High School, University).
        slideCount (int): Number of slides to generate (5-20 per PRD).
        text (str): The topic or context for the presentation.
        objectives (str, optional): Learning objectives.
        additional_comments (str, optional): Extra notes.
        objectives_file_url (str, optional): URL to a file with objectives.
        objectives_file_type (str, optional): Type of the objectives file (e.g., pdf, gdoc).
        additional_comments_file_url (str, optional): URL to a file with comments.
        additional_comments_file_type (str, optional): Type of the comments file.
        verbose (bool): Enable detailed logging for debugging.

    Returns:
        dict: The generated outline in JSON format.

    Raises:
        ToolExecutorError: If generation fails.
    """
    try:
        # Optional document loading (for context, though not used in outline_generator yet)
        docs = None
        if objectives_file_url and objectives_file_type:
            logger.info(f"Generating docs from {objectives_file_type}")
            docs = get_docs(objectives_file_url, objectives_file_type, verbose)
        if additional_comments_file_url and additional_comments_file_type:
            logger.info(f"Generating docs from {additional_comments_file_type}")
            additional_docs = get_docs(additional_comments_file_url, additional_comments_file_type, verbose)
            docs = docs + additional_docs if docs and additional_docs else additional_docs or docs

        # Generate outline (this core.py is only for outline in your friend's setup)
        output = outline_executor(
            instructionalLevel=instructionalLevel,
            slideCount=slideCount,
            text=text,
            objectives=objectives,
            additional_comments=additional_comments,
            verbose=verbose
        )
        logger.info("Outline generated successfully")
        return output

    except LoaderError as e:
        error_message = str(e)
        logger.error(f"Error in Presentation Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)