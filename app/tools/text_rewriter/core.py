from app.services.logger import setup_logger
from app.tools.text_rewriter.tools import TextRewriter
from app.utils.document_loaders import get_docs
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

ALLOWED_FILE_TYPES = {"pptx", "pdf", "docx", "txt", "csv", "youtube_url", "url", "gsheet"}

def executor(raw_text: str,
             rewrite_instructions: str,
             file_url: str,
             file_type: str,
             lang: str,
             verbose: bool = True):
    
    try:
        docs = None
        
        if file_type and file_url:
            if verbose:
                logger.info(f"File URL loaded: {file_url}")
            if file_type in ALLOWED_FILE_TYPES:
                docs = get_docs(file_url, file_type, lang, verbose=True)
            else:
                raise ToolExecutorError(f"File type {file_type} not supported")

        output = TextRewriter(rewrite_instructions, lang, verbose=verbose).rewrite(raw_text, docs)
    
    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output
