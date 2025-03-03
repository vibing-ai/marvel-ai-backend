
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.utils.document_loaders import get_docs
from app.tools.outline_generator.tools import OutlineGenerator
from app.services.schemas import OutlineGeneratorArgs

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
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import OutlineGeneratorArgs
from app.utils.document_loaders import get_docs
from app.tools.outline_generator.tools import OutlineGenerator

logger = setup_logger()

def executor(
    context: str,
    level: str,
    num_slides: int,
    reference_material_file_url: str = None,
    reference_material_file_type: str = None,
    verbose: bool = False,
):
    """
    Execute outline generation and return the generated outline.
    
    Args:
        context: Topic or context for the outline
        level: Educational level (elementary, middle, high, university, etc.)
        num_slides: Number of slides to generate in the outline
        reference_material_file_url: URL of reference material file
        reference_material_file_type: Type of reference material file
        verbose: Whether to enable verbose logging
    
    Returns:
        Generated outline with slide titles
    """
    try:
        if verbose:
            logger.info(f"Starting outline generation for: {context}")
            
        # Load documents if reference material is provided
        docs = None
        if reference_material_file_url and reference_material_file_type:
            if verbose:
                logger.info(f"Loading reference material from: {reference_material_file_url}")
            try:
                docs = get_docs(reference_material_file_url, reference_material_file_type)
                if verbose:
                    logger.info(f"Successfully loaded {len(docs)} document chunks")
            except Exception as e:
                logger.warning(f"Failed to load reference material: {str(e)}")
                logger.info("Continuing without reference material")
        
        # Create and run the outline generator
        outline_args = OutlineGeneratorArgs(
            context=context,
            level=level,
            num_slides=num_slides
        )
        
        output = OutlineGenerator(args=outline_args, verbose=verbose).create_outline(docs)
        
        logger.info(f"Outline generated successfully with {len(output['slides'])} slides")
        return output
        
    except LoaderError as e:
        error_message = str(e)
        logger.error(f"Error in Outline Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in outline generator executor: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)
