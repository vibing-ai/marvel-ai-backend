from app.api.error_utilities import LoaderError, ToolExecutorError
from typing import List
from app.services.schemas import SlideGeneratorInput
from app.tools.presentation_generator_updated.slide_generator.tools import SlideGenerator
from app.services.logger import setup_logger
from .image_utils import build_prompt, call_image_api, get_image_size  # ✅ import image utils

logger = setup_logger()

def executor(
             slides_titles: List[str],
             topic: str,
             instructional_level: str,
             lang: str, 
             verbose=False):
    try: 
        if not (slides_titles and topic and instructional_level):
            logger.info(f"Missing required inputs.")
            raise ValueError("Missing required inputs")
         
        logger.info(f"Generating slide outlines from '{topic}' for '{instructional_level}' level.")
        
        slide_generator_args = SlideGeneratorInput(
            slides_titles=slides_titles,
            instructional_level=instructional_level, 
            topic=topic,
            lang=lang
        )

        output = SlideGenerator(args=slide_generator_args, verbose=verbose).generate_slides()

        # ✅ Loop through each slide and attach image_url
        for slide in output.get("slides", []):
            title = slide.get("title", "")
            content = slide.get("content", [])
            layout = slide.get("template", "titleBullets")

            prompt = build_prompt(title, content, layout)
            width, height = get_image_size(layout)
            image_url = call_image_api(prompt, width, height)

            slide["image_url"] = image_url  # ✅ attach the generated image

        logger.info("Slides generated successfully with images.")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Slide Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output
