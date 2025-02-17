from fastapi.testclient import TestClient
from main import app  
from app.services.tool_registry import validate_inputs
import pytest
import os

#export PYTHONPATH=/path/to/your/project:$PYTHONPATH
#pytest -v

@pytest.fixture(scope='session', autouse=True)
def set_env_vars():
    # Backup old values and set new ones
    old_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    old_env_type = os.getenv('ENV_TYPE')
    old_project_id = os.getenv('PROJECT_ID')
    # Set new values
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'local-auth.json'
    os.environ['ENV_TYPE'] = 'dev'
    os.environ['PROJECT_ID'] = "kai-ai-f63c8"
    # Ensure these changes are only present during the tests
    yield
    # Restore old values after tests
    if old_creds:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = old_creds
    if old_env_type:
        os.environ['ENV_TYPE'] = old_env_type
    if old_project_id:
        os.environ['PROJECT_ID'] = old_project_id

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_validate_inputs_all_valid():
    # This mimics the structure that would be created in the endpoint
    # from request_data.inputs where each input is an instance with a name and value attribute
    request_inputs = [
        {"name": "topic", "value": "Quantum Mechanics"}, 
        {"name": "num_questions", "value": 5}
    ]
    
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    
    # Convert request_inputs to the dictionary format expected by validate_inputs
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    
    assert validate_inputs(request_inputs_dict, firestore_data) == True

def test_validate_inputs_missing_input():
    request_inputs = [
        {"name": "topic", "value": "Quantum Mechanics"}
    ]
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    assert validate_inputs(request_inputs_dict, firestore_data) == False

def test_validate_inputs_invalid_type():
    request_inputs = [
        {"name": "topic", "value": "Quantum Mechanics"}, 
        {"name": "num_questions", "value": "five"}
    ]
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    assert validate_inputs(request_inputs_dict, firestore_data) == False

def test_validate_inputs_extra_undefined_input():
    request_inputs = [
        {"name": "topic", "value": "Quantum Mechanics"}, 
        {"name": "num_questions", "value": 5},
        {"name": "extra_input", "value": "Extra Value"}
    ]
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    assert validate_inputs(request_inputs_dict, firestore_data) == True

def test_validate_inputs_input_not_found():
    request_inputs = [
        {"name": "unknown_input", "value": "Some Value"}
    ]
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    assert validate_inputs(request_inputs_dict, firestore_data) == False

