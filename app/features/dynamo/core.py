from app.services.logger import setup_logger
from app.features.dynamo.tools import get_summary, summarize_transcript_youtube_url, generate_flashcards, generate_concepts_from_img
from app.api.error_utilities import ToolExecutorError, VideoTranscriptError

logger = setup_logger(__name__)

SUPPORTED_FILE_TYPES = [
    'pdf', 'csv', 'txt', 'md', 'url', 'pptx', 'docx', 'xls', 'xlsx', 'xml',
    'gdoc', 'gsheet', 'gslide', 'gpdf'
]

def executor(file_url: str, file_type: str, lang: str = "en", verbose=False):
    try:
        if verbose:
            print(f"File URL loaded: {file_url}")
        
        flashcards = []

        if file_type == "img":
            flashcards = generate_concepts_from_img(file_url, lang)
        elif file_type == 'youtube_url':
            summary = summarize_transcript_youtube_url(file_url, verbose=verbose)
            flashcards = generate_flashcards(summary, lang, verbose)
        elif file_type in SUPPORTED_FILE_TYPES:
            summary = get_summary(file_url, file_type, verbose=verbose)
            flashcards = generate_flashcards(summary, lang, verbose)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            raise ValueError(f"Unsupported file type: {file_type}")
        
        sanitized_flashcards = []
        for flashcard in flashcards:
            if 'concept' in flashcard and 'definition' in flashcard:
                sanitized_flashcards.append({
                    "concept": flashcard['concept'],
                    "definition": flashcard['definition']
                })
            else:
                logger.warning(f"Malformed flashcard skipped: {flashcard}")

        return sanitized_flashcards

    except VideoTranscriptError as e:
        error_message = e
        logger.error(f"Error processing video transcript: {e}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(f"An error occurred while processing the file: {e}")
        raise ValueError(error_message)