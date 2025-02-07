from app.features.text_rewriter.tools import AITextRewriter
from app.utils.document_loaders import get_docs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import AITextRewriterArgs

logger = setup_logger()


def executor(
        original_text: str,
        instruction: str,
        file_url: str,
        file_type: str,
        lang: str,
        verbose=False
):
    try:
        logger.info(f"Generating docs. from {file_type}")

        if (file_url and file_type):
            logger.info(f"Generating docs. from {file_type}")
            docs = get_docs(file_url, file_type, True)
        else:
            docs = None

        ai_text_rewriter_args = AITextRewriterArgs(
            original_text=original_text,
            instruction=instruction,
            file_type=file_type,
            file_url=file_url,
            lang=lang
        )

        output = AITextRewriter(args=ai_text_rewriter_args, verbose=verbose).rewrite_text(docs)

        logger.info(f"AI-TextRewriter rewrote a text successfully")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in AI Resistant Assignment Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output
