from typing import Optional
from app.services.logger import setup_logger
from app.tools.image_generator.tool import ImageGenerator
from app.tools.image_generator.schemas import ImageGeneratorArgs

from app.api.error_utilities import  ImageGenerationError
import google.auth

logger = setup_logger(__name__)

def executor(
    prompt: str,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    presets: Optional[dict] = None,
    lang: str = "en",
    verbose: bool = True
) -> dict:
    """
    Main executor function for image generation    
    Args:
        prompt (str): The main prompt for image generation
        subject (str, optional): Educational subject
        grade_level (str, optional): Target grade level
        style (str, optional): Desired image style
        size (str, optional): Image size
        verbose (bool): Enable verbose logging        
    Returns:
        dict: Generated image information including URL and metadata
    """
    try:
        # Initialize configuration
      #  config = ImageGeneratorConfig(verbose=verbose)
        
        # Create arguments object

        args = ImageGeneratorArgs(
            prompt=prompt,
            subject=subject,
            grade_level=grade_level,
            presets=presets,
            lang=lang,
        )

        logger.info(f"Generating image with prompt: {prompt}")
        # Initialize generator and generate image
        generator = ImageGenerator(args=args, verbose=verbose)
        result = generator.generate_image()    
        
    
    
    except ImageGenerationError as e:
        error_message = str(e)
        logger.error(f"Image Generation Error: {error_message}")
        raise ImageGenerationError(error_message)
    except ValueError as e:
        error_message = f"Value Error: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    if result.get("image_url"):
        logger.info(f"Image generated successfully: {result['image_url']}")
    else:
        logger.error(f"Image generation failed: {result.get('error', 'Unknown error')}")
    return result

