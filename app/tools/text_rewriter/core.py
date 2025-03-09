import logging
from typing import List, Optional
from app.tools.text_rewriter.tools import read_file, rewrite_text
from app.tools.text_rewriter.tools import file_to_text_converter

logger = logging.getLogger(__name__)

def executor(instructions: str, input_text: Optional[str] = None, file_url: Optional[str] = None, file_type: Optional[str] = None, verbose: Optional[bool] = False) -> str:
    """
    The executor function to handle input data and instructions, process the file if provided,
    and rewrite the text according to the instructions.

    Parameters:
    - instructions (str): Rewriting instructions.
    - file_url (Optional[str]): URL of the file to be uploaded.
    - file_type (Optional[str]): Type of the file to be uploaded (e.g., csv, pdf, docx).
    
    Returns:
    - str: The rewritten text based on the instructions and input data.
    """
    try:
        # Step 1: Read input text from file if provided
        #input_text = ""
        if file_url and file_type:
            input_text = read_file(file_url, file_type)

        # Step 2: Rewrite the text based on the provided instructions
        rewritten_text = rewrite_text(input_text or instructions, instructions)
        
        # Step 3: Return the rewritten text
        print(rewritten_text)
        return rewritten_text
    except Exception as e:
        logger.error(f"Error in text rewriting: {str(e)}")
        return "An error occurred during the rewriting process."


