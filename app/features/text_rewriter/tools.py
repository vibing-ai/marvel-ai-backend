from pydantic import BaseModel, create_model
import os
import json
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv("text_rewriter.env")  # Looks for the .env file by name

if dotenv_path:
    print(f"Found .env file at: {dotenv_path}")
    load_dotenv(dotenv_path)  # Load the environment variables from the found .env file
else:
    print("No .env file found!")

api_key = os.getenv("GOOGLE_API_KEY")
project_id = os.getenv("PROJECT_ID")

if not api_key or not project_id:
    raise ValueError("API key or project ID is missing in environment variables.")

def create_input_schema(metadata: dict):
    """
    Dynamically creates a Pydantic model for input validation based on metadata.json.

    Args:
        metadata (dict): Metadata defining the inputs.

    Returns:
        BaseModel: A Pydantic schema for input validation.
    """
    fields = {
        input_name: (str, ...) if input_spec["required"] else (str, None)
        for input_name, input_spec in metadata["inputs"].items()
    }
    return create_model(metadata["name"] + "InputSchema", **fields)

def create_output_schema(metadata: dict):
    """
    Dynamically creates a Pydantic model for output validation based on metadata.json.

    Args:
        metadata (dict): Metadata defining the outputs.

    Returns:
        BaseModel: A Pydantic schema for output validation.
    """
    fields = {
        output_name: (str, ...)
        for output_name, output_spec in metadata["outputs"].items()
    }
    return create_model(metadata["name"] + "OutputSchema", **fields)

def get_few_shot_examples() -> str:
    """
    Returns a string containing a set of few-shot examples for text rewriting tasks.
    Reads from the 'few_shot_examples.txt' file located in the 'prompt/' folder.
    """
    # Define the path to the prompt folder and the few-shot examples file
    prompt_file_path = os.path.join(os.path.dirname(__file__), "prompt", "few_shot_examples.txt")

    try:
        with open(prompt_file_path, "r") as file:
            few_shot_examples = file.read()
    except FileNotFoundError:
        raise ValueError(f"Few-shot examples file not found at {prompt_file_path}")
    
    return few_shot_examples

def rewrite_tool_handler(inputs: dict, few_shot_examples: str):
    """
    Handles the text rewriting tool request by validating inputs and executing the model.
    """
    try:
        metadata = load_metadata()  # Load the metadata
        validate_inputs(inputs, metadata)  # Validate inputs using the metadata

        # Initialize the model and pipeline
        model = GoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.7,
            max_output_tokens=1024,
            api_key=api_key  # Using the globally loaded API key
        )

        # Define the prompt template using few-shot examples
        prompt_template = PromptTemplate(
            template=(
                "{few_shot_examples}\n"
                "Task: {instructions}\n\n"
                "Text: {text}\n\n"
                "Respond with a JSON object containing only the key 'rewritten_text' and its value."
            ),
            input_variables=["instructions", "text", "few_shot_examples"]
        )

        output_parser = JsonOutputParser(pydantic_object=dict)

        # Combine components into the pipeline
        pipeline = prompt_template | model | output_parser

        # Prepare the input for the model
        inputs["few_shot_examples"] = few_shot_examples

        # Execute the pipeline and return the result
        result = pipeline.invoke(inputs)
        
        return {"rewritten_text": result.get("rewritten_text", "No rewritten text found")}

    except Exception as e:
        raise ValueError(f"Error in rewrite_tool_handler: {str(e)}")

def load_metadata():
    """
    Loads metadata from the metadata.json file.

    Returns:
        dict: The metadata for the text rewriter tool.
    """
    METADATA_FILE = os.path.join(os.path.dirname(__file__), "metadata.json")
    with open(METADATA_FILE, "r") as f:
        return json.load(f)

def validate_inputs(inputs: dict, metadata: dict):
    """
    Validates the inputs using the provided metadata.

    Args:
        inputs (dict): The input data to validate.
        metadata (dict): The metadata that defines the valid inputs.

    Raises:
        ValueError: If validation fails.
    """
    for input_key, input_spec in metadata["inputs"].items():
        if input_spec["required"] and input_key not in inputs:
            raise ValueError(f"Missing required input: {input_key}")
        if input_key in inputs and not isinstance(inputs[input_key], str):
            raise ValueError(f"Invalid type for input '{input_key}'. Expected: {input_spec['type']}")