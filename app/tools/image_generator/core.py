from app.services.logger import setup_logger
from app.tools.image_generator.tools import ImageGenerator, ImageGeneratorArgs
from app.api.error_utilities import ImageHandlerError, ToolExecutorError

logger = setup_logger(__name__)

def executor(
    prompt: str,
    subject: str = None,
    grade_level: str = None,
    lang: str = "en",
    verbose: bool = False
):
    """
    Executor function for the Image Generator tool.

    Args:
        prompt (str): The text prompt to generate an image from.
        subject (str, optional): The educational subject (e.g., 'math', 'science').
        grade_level (str, optional): The grade level (e.g., 'elementary', 'middle school', 'high school').
        lang (str, optional): The language for text in the image. Defaults to "en".
        verbose (bool, optional): Flag for verbose logging. Defaults to False.

    Returns:
        dict: Generated image data including base64 encoded image and metadata.
              If GCP storage is configured, the result will also include a gcp_url field.

    Raises:
        ToolExecutorError: If there's an error in the image generation process.
    """
    try:
        if verbose:
            logger.info(f"Generating image with prompt: {prompt}")
            if subject:
                logger.info(f"Subject: {subject}")
            if grade_level:
                logger.info(f"Grade level: {grade_level}")
            logger.info(f"Language: {lang}")

        # Create arguments for the image generator
        image_generator_args = ImageGeneratorArgs(
            prompt=prompt,
            subject=subject,
            grade_level=grade_level,
            lang=lang
        )

        # Initialize the image generator
        generator = ImageGenerator(args=image_generator_args, verbose=verbose)

        # Generate the image
        result = generator.generate_educational_image()

        # Log success
        logger.info(f"Image generated successfully for prompt: {prompt}")

        # Return the result as a dictionary
        # Use model_dump() instead of dict() for Pydantic v2 compatibility
        return result.model_dump()

    except ImageHandlerError as e:
        error_message = str(e)
        logger.error(f"Image Handler Error: {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in Image Generator: {str(e)}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)