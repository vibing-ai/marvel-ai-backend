from typing import List
from .tools import extract_text_from_input, parse_ideas_from_response, validate_input_format, get_chain
import logging

def executor(grade_level: str, assignment_input: str) -> List[dict]:
    """
    Parameters:
    - grade_level: "Pre-k", "Kindergarten", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th", "University"
    - assignment_input: file path or URL
    
    Returns:
    - List of dictionaries containing modifined assigments and explanations
    """
    logging.info("Starting execution for grade level: %s", grade_level)

    if not validate_input_format(assignment_input):
        logging.error("Unsupported File or URL format for Input: %s",assignment_input )
        raise ValueError("Unsupported File or URL format")
    
    original_text = extract_text_from_input(assignment_input)
    chain = get_chain()
    response = chain.invoke({"assignment_text": original_text, "grade_level": grade_level})
    assignment_ideas = parse_ideas_from_response(response, grade_level)


    logging.info("Ideas generated successfully")
    return assignment_ideas
