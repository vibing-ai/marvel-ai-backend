
from app.api.error_utilities import LoaderError, ToolExecutorError
from typing import List
from app.utils.document_loaders import get_docs
from app.tools.presentation_generator_updated.schemas import SlideGeneratorInput
from app.tools.presentation_generator_updated.slide_generator.tools import SlideGenerator
from app.services.logger import setup_logger
logger = setup_logger()


def executor(
             slides_titles: List[str],
             topic: str,
             instructional_level: str,
             file_url: str,
             file_type: str,
             lang: str, 
             verbose=False):
    try: 
        if (not (slides_titles and topic and instructional_level)):
            logger.info(f"Missing required inputs.")
            raise ValueError("Missing required inputs")
         
        if(slides_titles and topic and instructional_level):
            logger.info(f"Generating slide outlines. from {topic} for {instructional_level} level")
        
       
        slide_generator_args = SlideGeneratorInput(
            slides_titles=slides_titles,
            instructional_level=instructional_level, 
            topic=topic,
            file_url=file_url,
            file_type=file_type,
            lang=lang
        )


        #get the docs
        docs = None        

        def fetch_docs(file_url, file_type):
            return get_docs(file_url, file_type, True) if file_url and file_type else None

        docs = fetch_docs(file_type=file_type, file_url=file_url)
        logger.info("fetched docs")
        logger.info(f"Slidess: {slides_titles}")
        output = SlideGenerator(args=slide_generator_args, verbose=verbose).generate_slides(docs)
        
        logger.info(f"Slides generated successfully")
    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Slide Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    return output