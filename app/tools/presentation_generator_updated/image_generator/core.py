from app.api.error_utilities import LoaderError, ToolExecutorError
from typing import Union, Dict, List, Any
from app.tools.presentation_generator_updated.image_generator.tools import ImageGenerator
from app.services.logger import setup_logger

logger = setup_logger(__name__)

def executor(
        slide_id: int,
        title: str,
        content: Union[str, list, dict],
        layout: str,
        image_model: str = "flux",
        verbose: bool = False
    ):
    """
    Executor function for generating images for presentation slides.
    
    Args:
        slide_id (int): The slide ID
        title (str): The slide title
        content (Union[str, list, dict]): The slide content (can be various formats)
        layout (str): The slide layout/template
        image_model (str, optional): The image generation model to use. Defaults to "flux".
        verbose (bool, optional): Whether to log verbose output. Defaults to False.
        
    Returns:
        str: Public URL to the generated image on Google Cloud Storage
        
    Raises:
        ToolExecutorError: If there's an error in the image generation process
        ValueError: If there's a general error or missing required inputs
    """
    try:
        if not (title and content and layout):
            logger.info("Missing required inputs for image generation.")
            raise ValueError("Missing required inputs: title, content, and layout are required")
        
        if verbose:
            logger.info(f"Generating image for slide {slide_id} with title '{title}' using {image_model} model")
        
        # Initialize the image generator with the specified model
        image_generator = ImageGenerator(image_model=image_model)
        
        # Generate the image
        image_url = image_generator.generate_slide_image(
            slide_id=slide_id,
            title=title,
            content=content,
            layout=layout
        )
        
        if verbose:
            logger.info(f"Image generated successfully: {image_url}")
        
        return image_url
    
    except LoaderError as e:
        error_message = str(e)
        logger.error(f"Error in Image Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in image generator executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)