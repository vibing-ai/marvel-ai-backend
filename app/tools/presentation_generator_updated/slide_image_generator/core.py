from typing import List, Dict
from app.services.logger import setup_logger
from app.tools.presentation_generator_updated.slide_image_generator.tools import SlideImageGenerator

logger = setup_logger(__name__)

def executor(slides: List[dict], verbose: bool = False) -> dict:
    """
    Execute the slide image generation process.
    
    Args:
        slides (List[dict]): List of slide dictionaries from the slide generator
        verbose (bool): Enable verbose logging
    
    Returns:
        dict: Dictionary containing processed slides with generated images
    """
    try:
        if verbose: 
            logger.info("Starting slide image generation process")
        generator = SlideImageGenerator(slides=slides, verbose=verbose)

        if verbose: 
            logger.info("Generating slides images")
        result = generator.generate_slides()
        
        if verbose: 
            logger.info("Slides images generated successfully")
        return result
        
    except Exception as e:
        error_message = f"Error in slide image generation: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)