import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.services.tool_registry import BaseTool, ToolInput, ToolFile
from fastapi import HTTPException
from app.api.tool_utilities import get_executor_by_name, load_tool_metadata, prepare_input_data, execute_tool

# Sample configuration for tools_config
tools_config = {
    "0": {
        "path": "features/quizzify",
        "executor": "features.quizzify.core.quizzify_executor",
        "metadata_file": "metadata.json"
    },
    "1": {
        "path": "features/dynamo",
        "executor": "features.dynamo.core.dynamo_executor",
        "metadata_file": "metadata.json"
    }
}

# Mock data for load_tool_metadata
metadata = {
    "inputs": {
        "topic": "Math",
        "num_questions": 1
    }
}

@patch('builtins.__import__')
def test_get_executor_by_name(mock_import):
    # Setup the MagicMock for module and function
    mock_module = MagicMock()
    mock_function = MagicMock(return_value="function result")
    mock_module.executor = mock_function
    mock_import.return_value = mock_module

    # The function name 'executor' is standardized across modules
    executor = get_executor_by_name("features.quizzify.core")
    
    # Check if the correct function is retrieved
    assert executor() == "function result"
    mock_function.assert_called_once()  # Ensuring that the function setup is being called correctly

@patch('os.path.exists')
@patch('os.path.getsize')
@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(metadata))
def test_load_tool_metadata_success(mock_file, mock_getsize, mock_exists):
    mock_exists.return_value = True
    mock_getsize.return_value = 100  # simulate non-empty file

    data = load_tool_metadata("0")
    assert data == metadata  # assert that returned data matches the mock metadata

@patch('os.path.exists', return_value=False)
def test_load_tool_metadata_not_found(mock_exists):
    with pytest.raises(HTTPException) as exc_info:
        load_tool_metadata("0")
    assert exc_info.value.status_code == 404

def test_prepare_input_data():
    request_data = BaseTool(
        tool_id=0,
        inputs=[
            ToolInput(name="topic", value="Math"),
            ToolInput(name="num_questions", value=1),
            ToolInput(name="files", value=[{"filePath": "path/to/file", "filename": "file.pdf", "url": "http://example.com"}])
        ]
    )

    expected = {
        "topic": "Math",
        "num_questions": 1,
        "files": [ToolFile(filePath="path/to/file", filename="file.pdf", url="http://example.com")]
    }

    result = prepare_input_data(request_data)
    assert result['topic'] == expected['topic']
    assert result['num_questions'] == expected['num_questions']
    assert isinstance(result['files'][0], ToolFile)
    assert result['files'][0].url == "http://example.com"


@patch('api.tool_utilities.get_executor_by_name')
def test_execute_tool_success(mock_get_executor):
    tool_id = "0"
    request_inputs_dict = {"verbose": True}
    mock_function = MagicMock(return_value="execution result")

    mock_get_executor.return_value = mock_function

    result = execute_tool(tool_id, request_inputs_dict)
    assert result == "execution result"
    mock_function.assert_called_once_with(**request_inputs_dict)

@patch('api.tool_utilities.get_executor_by_name', side_effect=ImportError("Function not found"))
def test_execute_tool_failure(mock_get_executor):
    tool_id = "0"
    request_inputs_dict = {"verbose": True}
    with pytest.raises(HTTPException) as exc_info:
        execute_tool(tool_id, request_inputs_dict)
    assert exc_info.value.status_code == 500
    assert "Function not found" in str(exc_info.value.detail)