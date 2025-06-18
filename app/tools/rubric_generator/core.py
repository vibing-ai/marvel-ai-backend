from typing import Optional
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import RubricGeneratorArgs
from app.utils.document_loaders import get_docs
from app.tools.rubric_generator.tools import RubricGenerator

logger = setup_logger()

def validate_file_type(file_type: Optional[str], field_name: str) -> None:
    """Validate that the file type is supported."""
    if not file_type:
        return
        
    supported_types = ["csv", "pdf", "docx", "pptx", "txt", "youtube", "website", "gsheet"]
    if file_type.lower() not in supported_types:
        raise ValueError(
            f"Unsupported file type '{file_type}' for {field_name}. "
            f"Supported types are: {', '.join(supported_types)}"
        )

def executor(
    grade_level: str,
    point_scale: int,
    objectives: Optional[str] = None,
    assignment_description: Optional[str] = None,
    additional_customization: Optional[str] = None,
    objectives_file_url: Optional[str] = None,
    objectives_file_type: Optional[str] = None,
    assignment_description_file_url: Optional[str] = None,
    assignment_description_file_type: Optional[str] = None,
    lang: str = "en",
    verbose: bool = False
) -> dict:
    """
    Generate a rubric based on the provided parameters.
    
    Args:
        grade_level: The grade level for the rubric (e.g., '9th Grade')
        point_scale: The number of performance levels in the rubric (typically 3-6)
        objectives: Learning standards or objectives for the assignment
        assignment_description: Detailed description of the assignment
        additional_customization: Any additional customization or specific requirements
        objectives_file_url: URL to a file containing standards/objectives
        objectives_file_type: Type of the objectives file
        assignment_description_file_url: URL to a file containing assignment description
        assignment_description_file_type: Type of the assignment description file
        lang: Language code for the rubric (e.g., 'en', 'es', 'fr')
        verbose: Whether to log verbose output
        
    Returns:
        dict: The generated rubric
        
    Raises:
        ValueError: If any of the inputs are invalid
        ToolExecutorError: If there's an error generating the rubric
    """
    try:
        # Validate inputs
        if not grade_level:
            raise ValueError("Grade level is required")
            
        if not isinstance(point_scale, int) or point_scale < 2 or point_scale > 10:
            raise ValueError("Point scale must be an integer between 2 and 10")
            
        if not objectives and not objectives_file_url:
            raise ValueError("Either objectives or objectives_file_url must be provided")
            
        if not assignment_description and not assignment_description_file_url:
            raise ValueError("Either assignment_description or assignment_description_file_url must be provided")
        
        # Validate file types
        if objectives_file_url:
            validate_file_type(objectives_file_type, "objectives_file_type")
            logger.info(f"Generating docs from objectives file: {objectives_file_type}")
            
        if assignment_description_file_url:
            validate_file_type(assignment_description_file_type, "assignment_description_file_type")
            logger.info(f"Generating docs from assignment description file: {assignment_description_file_type}")

        # Fetch documents from URLs if provided
        def fetch_docs(file_url: str, file_type: str) -> list:
            if not file_url or not file_type:
                return []
                
            try:
                # Handle different URL types
                if file_type == "youtube":
                    # YouTube URL processing would go here
                    # For now, just return an empty list as a placeholder
                    return []
                elif file_type == "website":
                    # Website URL processing would go here
                    return []
                elif file_type == "gsheet":
                    # Google Sheets processing would go here
                    return []
                else:
                    # For regular file types, use the document loader
                    return get_docs(file_url, file_type, True)
            except Exception as e:
                logger.error(f"Error loading document from {file_url}: {str(e)}")
                raise ToolExecutorError(f"Failed to load document: {str(e)}")

        # Fetch documents from both sources
        objectives_docs = fetch_docs(objectives_file_url, objectives_file_type) if objectives_file_url else []
        assignment_desc_docs = fetch_docs(assignment_description_file_url, assignment_description_file_type) if assignment_description_file_url else []
        
        # Combine all documents
        docs = objectives_docs + assignment_desc_docs
        
        # Create and return the Rubric
        rubric_generator_args = RubricGeneratorArgs(
            grade_level=grade_level,
            point_scale=point_scale,
            objectives=objectives or "",
            assignment_description=assignment_description or "",
            additional_customization=additional_customization or "",
            objectives_file_url=objectives_file_url or "",
            objectives_file_type=objectives_file_type or "",
            assignment_description_file_url=assignment_description_file_url or "",
            assignment_description_file_type=assignment_description_file_type or "",
            lang=lang
        )
        
        output = RubricGenerator(args=rubric_generator_args, verbose=verbose).create_rubric(docs)
        logger.info("Rubric generated successfully")
        return output
    
    except LoaderError as e:
        error_message = f"Error loading document: {str(e)}"
        logger.error(f"Error in Rubric Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in rubric generator: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)