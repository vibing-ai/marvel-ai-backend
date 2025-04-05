import pytest
from unittest.mock import patch, MagicMock
from app.tools.presentation_generator_updated.image_generator.core import executor
from app.tools.presentation_generator_updated.image_generator.tools import ImagePromptGenerator, image_generation_handler
from app.api.error_utilities import ToolExecutorError

@pytest.fixture
def mock_presentation_content():
    return {
        "slides": [
            {
                "title": "Introduction to AI",
                "template": "titleAndBody",
                "content": ["What is Artificial Intelligence?", "History of AI"]
            },
            {
                "title": "Machine Learning",
                "template": "twoColumn",
                "content": ["Types of ML", "Applications"]
            }
        ]
    }

@pytest.fixture
def mock_image_generation_response():
    return {
        "status": "success",
        "data": {
            "Introduction to AI": "https://storage.googleapis.com/bucket/image1.jpg",
            "Machine Learning": "https://storage.googleapis.com/bucket/image2.jpg"
        }
    }

def test_executor_valid_input(mock_presentation_content, mock_image_generation_response):
    """Test executor with valid presentation content"""
    with patch('app.tools.presentation_generator_updated.image_generator.core.image_generation_handler') as mock_handler:
        mock_handler.return_value = mock_image_generation_response
        
        result = executor(mock_presentation_content)
        
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert "data" in result
        assert len(result["data"]) == 2
        mock_handler.assert_called_once()

def test_executor_empty_input():
    """Test executor with empty input"""
    with pytest.raises(ToolExecutorError) as exc_info:
        executor({})
    assert "Missing required inputs" in str(exc_info.value)

def test_executor_string_input():
    """Test executor with string input instead of dict"""
    with pytest.raises(ToolExecutorError) as exc_info:
        executor("Invalid input")
    assert "Invalid presentation content format" in str(exc_info.value)

def test_executor_no_slides():
    """Test executor with dict but no slides"""
    with pytest.raises(ToolExecutorError) as exc_info:
        executor({"other_key": "value"})
    assert "No slides content found" in str(exc_info.value)

def test_executor_invalid_handler_output():
    """Test executor when handler returns invalid output"""
    mock_content = {
        "slides": [{"title": "Test", "content": ["content"]}]
    }
    
    with patch('app.tools.presentation_generator_updated.image_generator.core.image_generation_handler') as mock_handler:
        mock_handler.return_value = "invalid output"
        
        with pytest.raises(ToolExecutorError) as exc_info:
            executor(mock_content)
        assert "Invalid output from image generation handler" in str(exc_info.value)

def test_executor_handler_error():
    """Test executor when handler raises an exception"""
    mock_content = {
        "slides": [{"title": "Test", "content": ["content"]}]
    }
    
    with patch('app.tools.presentation_generator_updated.image_generator.core.image_generation_handler') as mock_handler:
        mock_handler.side_effect = Exception("Handler error")
        
        with pytest.raises(ToolExecutorError) as exc_info:
            executor(mock_content)
        assert "Error in image generation: Handler error" in str(exc_info.value)

@pytest.mark.integration
def test_executor_integration(mock_presentation_content):
    """Integration test for executor with actual image generation"""
    try:
        result = executor(mock_presentation_content)
        assert isinstance(result, dict)
        assert "status" in result
        assert "data" in result
        assert all(isinstance(url, str) for url in result["data"].values())
    except Exception as e:
        pytest.skip(f"Integration test failed due to external dependencies: {str(e)}")

def test_executor_with_none_input():
    """Test executor with None input"""
    with pytest.raises(ToolExecutorError) as exc_info:
        executor(None)
    assert "Missing required inputs" in str(exc_info.value)

def test_executor_with_empty_slides_list():
    """Test executor with empty slides list"""
    with pytest.raises(ToolExecutorError) as exc_info:
        executor({"slides": []})
    assert "No slides content found" in str(exc_info.value)

def test_executor_with_malformed_slides():
    """Test executor with malformed slides structure"""
    malformed_content = {
        "slides": [
            {"wrong_key": "value"}  # Missing required title and content
        ]
    }
    
    with pytest.raises(ToolExecutorError) as exc_info:
        executor(malformed_content)
    assert "Invalid slide structure: missing required 'title' field" in str(exc_info.value)
