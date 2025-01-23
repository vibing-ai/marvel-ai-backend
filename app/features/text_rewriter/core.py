from app.services.logger import setup_logger
from app.utils.document_loaders import get_docs
from app.features.text_rewriter.tools import TextRewriter
from app.api.error_utilities import ToolExecutorError
import langchain

logger = setup_logger()

ALLOWED_FILE_TYPES = {"pptx", "pdf", "docx", "txt", "csv", "youtube_url", "url", "gsheet"}

def executor(
             raw_text: str,
             instructions: str,
             file_url: str,
             file_type: str, 
             verbose=False):
    
    try:
        if verbose: logger.info(f"File URL loaded: {file_url}")
        
        if file_type and file_url and file_type in ALLOWED_FILE_TYPES:
            logger.info(f"Generating docs. from {file_url} with type {file_type}")
            docs = get_docs(file_url, file_type, verbose=True)
        elif raw_text:
            docs = None
        else:
            if file_type not in ALLOWED_FILE_TYPES:
                raise ToolExecutorError(f"File type {file_type} not supported")
            raise ToolExecutorError("File URL and file type must be provided")
        
        output = TextRewriter(instructions, verbose=verbose).rewrite(raw_text, docs)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output

