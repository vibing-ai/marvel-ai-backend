from app.services.logger import setup_logger
from app.tools.syllabus_generator.tools import SyllabusRequestArgs
from app.tools.syllabus_generator.tools import generate_syllabus
from app.utils.document_loaders_summarization import (
    generate_summary_from_img,
    summarize_transcript_youtube_url,
    get_summary
)
from app.api.error_utilities import SyllabusGeneratorError
from app.services.schemas import SyllabusGeneratorArgsModel

logger = setup_logger()

def executor(grade_level: str,
             subject: str,
             course_description: str,
             objectives: str,
             required_materials: str,
             grading_policy: str,
             policies_expectations: str,
             course_outline: str,
             additional_notes: str,
             file_url: str,
             file_type: str,
             lang: str,
             unit_time: str = "Week",           # New: Default unit of time
             unit_time_value: int = 10,         # New: Default unit value
             start_date: str = "2025-03-01",   # New: Default start date
             verbose: bool = True):
    
    if verbose:
        logger.info(f"File URL loaded: {file_url}")
    
    try:
        # Generate summary based on file type
        if file_type == 'img':
            summary = generate_summary_from_img(file_url)
        elif file_type == 'youtube_url':
            summary = summarize_transcript_youtube_url(file_url, verbose=verbose)
        else:
            summary = get_summary(file_url, file_type, verbose=verbose)
    
        # Update SyllabusGeneratorArgsModel to include new fields
        syllabus_args_model = SyllabusGeneratorArgsModel(
            grade_level=grade_level,
            subject=subject,
            course_description=course_description,
            objectives=objectives,
            required_materials=required_materials,
            grading_policy=grading_policy,
            policies_expectations=policies_expectations,
            course_outline=course_outline,
            additional_notes=additional_notes,
            file_url=file_url,
            file_type=file_type,
            lang=lang,
            # Pass new fields to the model (assumes model is updated)
            unit_time=unit_time,
            unit_time_value=unit_time_value,
            start_date=start_date
        )

        request_args = SyllabusRequestArgs(
            syllabus_args_model,
            summary
        )
        
        syllabus = generate_syllabus(request_args, verbose=verbose)

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {str(e)}")
        raise SyllabusGeneratorError(f"Failed to generate syllabus: {str(e)}") from e

    return syllabus