import json
import os
from datetime import datetime
import uuid
import time
from app.services.logger import setup_logger
from app.services.tool_registry import ToolFile
from app.api.error_utilities import VideoTranscriptError, InputValidationError, ToolExecutorError
from typing import Dict, Any, List, Union
from fastapi import HTTPException
from pydantic import ValidationError
import replicate # Image generation - flux dev
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

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
    module_dir_path = os.path.join(base_dir, '../..', *tool_config['path'].split('.')[:-1])  # Go one level up and then to the path
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

def finalize_inputs(input_data, validate_data: List[Dict[str, str]]) -> Dict[str, Any]:
    inputs = prepare_input_data(input_data)
    validate_inputs(inputs, validate_data)
    inputs = convert_files_to_tool_files(inputs)
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

templates_to_aspect_ratios = {
    "titleAndBody": "16:9",  # 1280x720
    "titleAndBullets": "4:3",  # 1024x768
    "twoColumn": "4:3",  # 800x600
    "sectionHeader": "16:9"  # 1600x900
}

def construct_image_generation_prompt(title: str, content: Union[str, list, dict], layout: str) -> str:
    """
    Constructs a detailed prompt for image generation based on slide content.
    Uses the slide_image_prompt.txt template and Google Gemini model to generate
    a high-quality image prompt.
    
    Args:
        title (str): The slide title
        content (str/list/dict): The slide content (can be various formats)
        layout (str): The slide layout/template
        
    Returns:
        str: A structured prompt for image generation
    """
    # Extract key elements from content based on its type
    content_text = ""
    if isinstance(content, str):
        content_text = content
    elif isinstance(content, list):
        content_text = ". ".join(content)
    elif isinstance(content, dict):
        if "leftColumn" in content and "rightColumn" in content:
            content_text = f"{content['leftColumn']}. {content['rightColumn']}"
    
    # Load the slide image prompt template
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        "presentation_generator_updated/slide_generator/prompt/slide_image_prompt.txt"
    )
    with open(prompt_path, 'r') as f:
        slide_image_prompt_template = f.read()
    prompt = PromptTemplate(
        template=slide_image_prompt_template,
        input_variables=["title", "content"]
    )
    
    # Generate the image prompt using Gemini
    model = GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    try:
        image_prompt_output = model.invoke(prompt.format(
            title=title,
            content=content_text
        ))

        return image_prompt_output
        
    except Exception as e:
        raise Exception(f"Error generating image prompt with Gemini: {str(e)}")

def generate_slide_image(title: str, content: Union[str, list, dict], layout: str, model: str = "flux") -> str:
    """
    Generates an image for a presentation slide and returns the URL.
    
    Args:
        title (str): The slide title
        content (str/list/dict): The slide content
        layout (str): The slide layout/template
        
    Returns:
        str: URL to the generated image
    """    
    try:
        # Get aspect ratio based on template
        aspect_ratio = templates_to_aspect_ratios.get(layout, "16:9")
        
        # Construct the prompt
        prompt = construct_image_generation_prompt(title, content, layout)
        logger.info(f"Generated image prompt: {prompt}...")
        
        # Call image generation API (Replicate's Flux model)
        input_params = {
            "prompt": prompt,
            "guidance": 7.5,
            "aspect_ratio": aspect_ratio
        }
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"slide_{timestamp}_{unique_id}.jpg"
        
        # Call the API
        logger.info(f"Calling image generation API for {model} model with aspect ratio: {aspect_ratio}")
        # time it
        start_time = time.time()
        if model == "flux":
            output = replicate.run(
                "black-forest-labs/flux-dev",
                input=input_params
            )
            end_time = time.time()
            logger.info(f"Flux image generation took {end_time - start_time} seconds")
            
            # For now, return the path to local image
            # In production, you would save this to Google Cloud Storage
            #image_url = output[0] if output and len(output) > 0 else ""
            #logger.info(f"Generated image URL: {image_url}")
            flux_output_dir = "flux_output"
            if not os.path.exists(flux_output_dir):
                os.makedirs(flux_output_dir)
            for index, item in enumerate(output):
                # get number of files in the folder
                num_files = len(os.listdir(flux_output_dir))
                with open(f"{flux_output_dir}/p{num_files + 1}.webp", "wb") as file:
                    file.write(item.read())
            num_files = len(os.listdir(flux_output_dir))
            return f"{flux_output_dir}/p{num_files}.webp"
        # Imagen
        else:
            # project_id = os.getenv("GCP_PROJECT_ID")
            # vertexai.init(project=project_id, location=location)

            imagen_output_dir = "imagen_output"
            if not os.path.exists(imagen_output_dir):
                os.makedirs(imagen_output_dir)

            model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")

            images = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                add_watermark=False,
            )

            images[0].save(location=f"{imagen_output_dir}/{filename}")
            num_files = len(os.listdir(imagen_output_dir))
            return f"{imagen_output_dir}/p{num_files}.jpg"

        
    except Exception as e:
        logger.error(f"Error generating slide image: {str(e)}")
        # Return a placeholder image if generation fails
        return f"https://via.placeholder.com/800x450.png?text={title.replace(' ', '+')}"
