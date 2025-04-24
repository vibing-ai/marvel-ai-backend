from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.tools.image_generator.tools import executor_image_generator
from app.tools.image_generator.schemas import ImageGenerationInput, ImageGenerationOutput
import os
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger()

def executor(base_prompt: str, grade_level: str, subject: str, language: str | None = None, verbose: bool = False):
    try:
        # Validate inputs using Pydantic model
        input_data = ImageGenerationInput(
            base_prompt=base_prompt,
            grade_level=grade_level,
            subject=subject,
            language=language
        )
        
        logger.info(f"Starting image generation with prompt: {input_data.base_prompt}, for a {input_data.grade_level}-level {input_data.subject} subject.")
        
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set.")
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        project_id = os.environ.get('PROJECT_ID')
        if not project_id:
            logger.error("PROJECT_ID environment variable not set.")
            raise ValueError("PROJECT_ID environment variable not set.")

        output = executor_image_generator(
            base_prompt=input_data.base_prompt,
            grade_level=input_data.grade_level,
            subject=input_data.subject,
            api_key=api_key,
            project_id=project_id,
            language=input_data.language,
            verbose=verbose
        )

        # Validate output using Pydantic model
        validated_output = ImageGenerationOutput(**output)
        return validated_output.dict()

    except Exception as e:
        logger.error(f"Error in image generator pipeline: {e}")
        raise ValueError(e)
