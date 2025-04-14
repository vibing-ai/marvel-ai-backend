from typing import Optional
from app.services.logger import setup_logger
from app.tools.image_generator.tool import ImageGenerator
from app.services.schemas import ImageGeneratorArgs
#from .schemas import ImageGeneratorArgs, ImageGeneratorResponse
#from .config import ImageGeneratorConfig

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
        logger.info(f"Image generation args: {args}")
        # Initialize generator and generate image
        generator = ImageGenerator(args=args, verbose=verbose)
        result = generator.generate_image()
        
        if verbose:
            logger.info(f"Successfully generated image with prompt: ")
        
        return result
    
    except Exception as e:
        logger.error(f"Error in image generation executor: {str(e)}")
        raise