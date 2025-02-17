import json
import os
from app.services.logger import setup_logger
from app.services.tool_registry import ToolFile
from app.api.error_utilities import VideoTranscriptError, InputValidationError, ToolExecutorError
from typing import Dict, Any, List
from fastapi import HTTPException
from pydantic import ValidationError
from app.services.schemas import WorksheetQuestionModel

logger = setup_logger(__name__)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "tools_config.json")
    with open(config_path, 'r') as f:
        return json.load(f)

tools_config = load_config()

def get_executor_by_name(module_path):
    try:
        module = __import__('app.'+module_path, fromlist=['executor'])
        return getattr(module, 'executor')
    except Exception as e:
        logger.error(f"Failed to import executor from {module_path}: {str(e)}")
        raise ImportError(f"Failed to import module from {module_path}: {str(e)}")

def load_tool_metadata(tool_id):
    logger.debug(f"Loading tool metadata for tool_id: {tool_id}")
    tool_config = tools_config.get(str(tool_id))
    
    if not tool_config:
        logger.error(f"No tool configuration found for tool_id: {tool_id}")
        raise HTTPException(status_code=404, detail="Tool configuration not found")
    
    # Ensure the base path is relative to the current file's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Base directory: {base_dir}")
    
    # Construct the directory path
    module_dir_path = os.path.join(base_dir, '..', *tool_config['path'].split('.')[:-1])  # Go one level up and then to the path
    module_dir_path = os.path.abspath(module_dir_path)  # Get absolute path
    logger.debug(f"Module directory path: {module_dir_path}")
    
    file_path = os.path.join(module_dir_path, tool_config['metadata_file'])
    logger.debug(f"Checking metadata file at: {file_path}")
    
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        logger.error(f"Metadata file missing or empty at: {file_path}")
        raise HTTPException(status_code=404, detail="Tool metadata not found")
    
    with open(file_path, 'r') as f:
        metadata = json.load(f)
        
    logger.debug(f"Loaded metadata: {metadata}")
    return metadata

def prepare_input_data(input_data) -> Dict[str, Any]:
    inputs = {input.name: input.value for input in input_data}
    return inputs

def check_missing_inputs(request_data: Dict[str, Any], validate_inputs: Dict[str, str]):
    for validate_input_name in validate_inputs:
        if validate_input_name not in request_data:
            error_message = f"Missing input: `{validate_input_name}`"
            logger.error(error_message)
            raise InputValidationError(error_message)

def raise_type_error(input_name: str, input_value: Any, expected_type: str):
    error_message = f"Input `{input_name}` must be a {expected_type} but got {type(input_value)}"
    logger.error(error_message)
    raise InputValidationError(error_message)

def validate_file_input(input_name: str, input_value: Any):
    if not isinstance(input_value, list):
        error_message = f"Input `{input_name}` must be a list of file dictionaries but got {type(input_value)}"
        logger.error(error_message)
        raise InputValidationError(error_message)
    
    for file_obj in input_value:
        if not isinstance(file_obj, dict):
            error_message = f"Each item in the input `{input_name}` must be a dictionary representing a file but got {type(file_obj)}"
            logger.error(error_message)
            raise InputValidationError(error_message)
        try:
            ToolFile.model_validate(file_obj, from_attributes=True)  # This will raise a validation error if the structure is incorrect
        except ValidationError:
            error_message = f"Each item in the input `{input_name}` must be a valid ToolFile where a URL is provided"
            logger.error(error_message)
            raise InputValidationError(error_message)

def validate_input_type(input_name: str, input_value: Any, expected_type: str):
    if expected_type == 'text' and not isinstance(input_value, str):
        raise_type_error(input_name, input_value, "string")
    elif expected_type == 'number' and not isinstance(input_value, (int, float)):
        raise_type_error(input_name, input_value, "number")
    elif expected_type == 'worksheet_list' and not isinstance(input_value, List):
        raise_type_error(input_name, input_value, "worksheet_list")
    elif expected_type == 'file':
        validate_file_input(input_name, input_value)

def validate_inputs(request_data: Dict[str, Any], validate_data: List[Dict[str, str]]) -> bool:
    validate_inputs = {input_item['name']: input_item['type'] for input_item in validate_data}
    
    # Check for missing inputs
    check_missing_inputs(request_data, validate_inputs)

    # Validate each input in request data against validate definitions
    for input_name, input_value in request_data.items():
        if input_name not in validate_inputs:
            continue  # Skip validation for extra inputs not defined in validate_inputs

        expected_type = validate_inputs[input_name]
        validate_input_type(input_name, input_value, expected_type)

    return True

def convert_files_to_tool_files(inputs: Dict[str, Any]) -> Dict[str, Any]:
    if 'files' in inputs:
        inputs['files'] = [ToolFile(**file_object) for file_object in inputs['files']]
    return inputs

def convert_worksheet_list_to_pydantic(inputs: Dict[str, Any]) -> Dict[str, Any]:
    if 'worksheet_list' in inputs:
        inputs['worksheet_list'] = WorksheetQuestionModel(worksheet_question_list = inputs['worksheet_list'])
    return inputs

def finalize_inputs(input_data, validate_data: List[Dict[str, str]]) -> Dict[str, Any]:
    inputs = prepare_input_data(input_data)
    validate_inputs(inputs, validate_data)
    inputs = convert_files_to_tool_files(inputs)
    inputs = convert_worksheet_list_to_pydantic(inputs)
    return inputs

def execute_tool(tool_id, request_inputs_dict):
    try:
        tool_config = tools_config.get(str(tool_id))
        
        if not tool_config:
            raise HTTPException(status_code=404, detail="Tool executable not found")
        
        execute_function = get_executor_by_name(tool_config['path'])
        request_inputs_dict['verbose'] = True
        
        return execute_function(**request_inputs_dict)
    
    except VideoTranscriptError as e:
        logger.error(f"Failed to execute tool due to video transcript error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except ToolExecutorError as e:
        logger.error(f"Failed to execute tool due to executor error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except ImportError as e:
        logger.error(f"Failed to execute tool due to import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Encountered error in executing tool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))