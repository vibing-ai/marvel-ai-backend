from app.utils.document_loaders import get_docs
from app.tools.presentation_generator.tools.outline_generator import OutlineGenerator
from app.services.schemas import PresentationGeneratorArgs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
             n_slides: int,
             topic: str,
             objectives: str,
             lang: str, 
             verbose=False):

    try:

        presentation_generator_args = PresentationGeneratorArgs(
            grade_level=grade_level,
            n_slides=n_slides,
            topic=topic,
            objectives=objectives,
            lang=lang
        )

        output = OutlineGenerator(args=presentation_generator_args, verbose=verbose).compile()

        logger.info(f"Presentation generated successfully")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Presentation Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output