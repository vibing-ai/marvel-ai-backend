
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import OutlineGeneratorArgs
from app.tools.outline_generator.tools import OutlineGeneratorPipeline

logger = setup_logger()

def executor(
        text_context:str,
        no_of_slides:int,
        instructional_level:str,
        lang:str,
        verbose=False):
    try:
        outline_generator_args=OutlineGeneratorArgs(
            text_context=text_context,
            no_of_slides=no_of_slides,
            instructional_level=instructional_level,
            lang=lang
        )
        output=OutlineGeneratorPipeline(args=outline_generator_args,verbose=verbose).generate_outline()
        logger.info(f"Generator by Prash  generated successfully")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Outline Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output
