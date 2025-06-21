from app.api.error_utilities import LoaderError, ToolExecutorError
from app.features.text_rewriter.tools import TextRewriterPipeline
from app.services.logger import setup_logger
from app.services.schemas import TextRewriterArgs
from app.utils.document_loaders import get_docs

logger = setup_logger()


def executor(
        text_input: str,
        file_type: str,
        file_url: str,
        rewrite_instruction: str,
        lang: str,
        verbose=False
):
    try:
        logger.info(f"Generating docs. from {file_type}")

        if not any([file_url, file_type, text_input]): raise ValueError("No input provided for text rewriter.")
        if not rewrite_instruction: raise ValueError("Rewrite instruction not provided.")

        if file_url and file_type:
            logger.info(f"Generating docs. from {file_type}")
            docs = get_docs(file_url, file_type, lang)
        else:
            docs = None

        # Initialize the TextRewriterArgs schema
        text_rewriter_args = TextRewriterArgs(
            text_input=text_input,
            file_type=file_type,
            file_url=file_url,
            rewrite_instruction=rewrite_instruction,
            lang=lang
        )

        output = TextRewriterPipeline(text_rewriter_args, verbose).rewrite_text(docs)

        logger.info(f"Text rewritten successfully.")

    except LoaderError as e:
        error_message = f"Error in Text Rewriter Pipeline ->: {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output
