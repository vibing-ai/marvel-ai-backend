from app.utils.document_loaders import get_docs
from app.services.logger import setup_logger
from app.tools.multiple_choice_quiz_generator.tools import QuizBuilder
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(topic: str,
             n_questions: int,
             file_url: str,
             file_type: str,
             lang: str,
             quiz_description: str,
             verbose=True):
    
    try:
        if verbose:
            logger.info(f"File URL loaded: {file_url}")

        docs = get_docs(file_url, file_type, lang, verbose=True)

        # Use quiz_description in the QuizBuilder
        output = QuizBuilder(topic, lang, quiz_description, verbose=verbose).create_questions(docs, n_questions)
    
    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output

