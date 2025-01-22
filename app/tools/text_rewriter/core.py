from typing import Union
import logging
from tools import process_input, apply_rewriting_logic, validate_input
import Langchain
def executor(input_data: Union[str, dict], instruction: str) -> str:
    """
    Main function to handle the text rewriting task.
    
    :param input_data: The input text or data to be rewritten (could be a string or a file).
    :param instruction: Instruction specifying how the text should be rewritten (e.g., simplify).
    :return: The rewritten text in the requested format.
    """
    try:
        # Validate the input
        if not validate_input(input_data, instruction):
            raise ValueError("Invalid input data or instruction.")
        
        # Process the input data (text or file) into a suitable format
        processed_data = process_input(input_data)
        
        # Apply the rewriting logic based on the instruction
        rewritten_text = apply_rewriting_logic(processed_data, instruction)
        
        return rewritten_text
    
    except Exception as e:
        logging.error(f"Error occurred during text rewriting: {e}")
        raise

