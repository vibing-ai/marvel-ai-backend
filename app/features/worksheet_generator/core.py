from typing import List
from app.services.logger import setup_logger
from app.features.worksheet_generator.tools import generate_course_type, worksheet_generator
from app.features.worksheet_generator.document_loaders import get_docs
from app.services.schemas import WorksheetQuestionModel

logger = setup_logger()

def executor(grade_level: str,
             topic: str,
             worksheet_list: WorksheetQuestionModel,
             file_url: str,
             file_type: str,
             lang: str,
             verbose=True):

    
    course_type = generate_course_type(topic, verbose)['course_type']

    if verbose:
        logger.info(f"Course Type: {course_type} [{lang}]")
        logger.info(f"File URL loaded: {file_url}")

    docs = get_docs(file_url, file_type, verbose)
    worksheet = worksheet_generator(course_type=course_type, 
                                    grade_level=grade_level, 
                                    worksheet_list=worksheet_list, 
                                    documents=docs, 
                                    lang=lang, 
                                    verbose=verbose)

    print(worksheet)
    return worksheet