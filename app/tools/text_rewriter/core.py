
from app.services.logger import setup_logger
from app.utils.document_loaders import get_docs
from app.api.error_utilities import LoaderError, ToolExecutorError
from .tools import TextRewriterPipeline, TextRewriterArgs

logger = setup_logger()

def executor(text: str,
             rewrite_style: str,
             file_url: str = None,
             file_type: str = None,
             lang: str = "en",
             verbose: bool = False):
    
    try:
        docs = None
        if file_url and file_type:
            logger.info(f"Generating docs from {file_type}")
            docs = get_docs(file_url, file_type, True)
            
        text_rewriter_args = TextRewriterArgs(
            text=text,
            rewrite_style=rewrite_style,
            file_url=file_url,
            file_type=file_type,
            lang=lang
        )

        output = TextRewriterPipeline(args=text_rewriter_args, verbose=verbose).rewrite_text(docs)
        logger.info("Text rewriting completed successfully")
        return output

    except LoaderError as e:
        logger.error(f"Error in Text Rewriter Pipeline -> {e}")
        raise ToolExecutorError(str(e))
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
