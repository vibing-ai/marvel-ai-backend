
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.utils.document_loaders import get_docs
from app.tools.outline_generator.tools import OutlineGenerator, OutlineGeneratorArgs

logger = setup_logger()

def executor(context: str,
             num_slides: int,
             level: str,
             file_url: str = None,
             file_type: str = None,
             lang: str = "en",
             verbose: bool = False):
    """
    Execute the outline generation process based on input parameters.
    
    Args:
        context: The topic or context for the outline
        num_slides: Number of slides to generate
        level: Instructional level (Elementary, Middle School, High School, University)
        file_url: Optional URL of a file with additional context
        file_type: Optional type of the file
        lang: Language for the outline, defaults to English
        verbose: Whether to log detailed information
        
    Returns:
        The generated outline as an OutlineOutput object
    """
    try:
        # Load documents if file URL and type are provided
        docs = None
        if file_url and file_type:
            logger.info(f"Generating docs from {file_type}")
            docs = get_docs(file_url, file_type, lang, verbose)
        
        # Create arguments for the outline generator
        outline_generator_args = OutlineGeneratorArgs(
            context=context,
            num_slides=num_slides,
            level=level,
            file_url=file_url,
            file_type=file_type,
            lang=lang
        )
        
        # Create and return the outline
        output = OutlineGenerator(args=outline_generator_args, verbose=verbose).create_outline(docs)
        
        logger.info("Outline generated successfully")
        return output
        
    except LoaderError as e:
        error_message = str(e)
        logger.error(f"Error in Outline Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
