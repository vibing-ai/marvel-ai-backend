from app.api.error_utilities import LoaderError, ToolExecutorError
from typing import List
from app.services.schemas import SlideGeneratorInput, ImageGeneratorInput
# from app.tools.presentation_generator_updated.slide_generator.tools import SlideGenerator
from app.tools.presentation_generator_updated.image_generator.tools import ImagePromptGenerator, image_generation_handler
from app.services.logger import setup_logger
logger = setup_logger()


def executor(presentation_content, verbose=False):
    try: 
        if not presentation_content:
            logger.info("Missing required inputs.")
            raise ValueError("Missing required inputs")
            
        # Extract the slides list from the dictionary if needed
        slides_list = (
            presentation_content["slides"] 
            if isinstance(presentation_content, dict) and "slides" in presentation_content
            else presentation_content
        )
        
        # Create ImageGeneratorInput with the correct format
        image_generator_args = ImageGeneratorInput(presentation_content=slides_list)
        output = image_generation_handler(image_generator_args)            # Reurns a dictionary of image titles and correswponding image URLs
        logger.info("Image generation completed successfully")
        
        return output
        
    except Exception as e:
        error_message = f"Error in image generation: {str(e)}"
        logger.error(error_message)
        
