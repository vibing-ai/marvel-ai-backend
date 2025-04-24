import pytest
import os
from unittest.mock import patch, MagicMock
from app.tools.image_generator.core import executor
from app.api.error_utilities import ToolExecutorError
from unittest.mock import patch
# --- Test Data --- #
VALID_PAYLOAD = {
    "base_prompt": "historical map",
    "grade_level": "High School",
    "subject": "History",
    "language": "English",
}

# --- Fixtures --- #
@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    """Setup environment variables needed for testing"""
    monkeypatch.setenv("GOOGLE_API_KEY", "fake_api_key")
    monkeypatch.setenv("PROJECT_ID", "fake_project_id")

@pytest.fixture
def mock_image_generator(monkeypatch):
    """Mock the image generator to return a fake URL"""
    mock = MagicMock(return_value={"image_url": "https://fake.storage/image.png"})
    monkeypatch.setattr("app.tools.image_generator.core.executor_image_generator", mock)
    return mock

# --- Success Cases --- #
def test_executor_success(mock_image_generator):
    """Test successful execution with valid inputs"""
    result = executor(**VALID_PAYLOAD, verbose=False)
    assert isinstance(result, dict)
    assert "image_url" in result
    assert result["image_url"] == "https://fake.storage/image.png"
    
    # Verify executor_image_generator was called with correct args
    mock_image_generator.assert_called_once()
    call_args = mock_image_generator.call_args[1]
    assert call_args["base_prompt"] == VALID_PAYLOAD["base_prompt"]
    assert call_args["grade_level"] == VALID_PAYLOAD["grade_level"]
    assert call_args["subject"] == VALID_PAYLOAD["subject"]
    assert call_args["language"] == VALID_PAYLOAD["language"]

def test_executor_with_verbose(mock_image_generator):
    """Test execution with verbose logging enabled"""
    result = executor(**VALID_PAYLOAD, verbose=True)
    assert isinstance(result, dict)
    assert "image_url" in result

# --- Environment Variable Tests --- #
def test_missing_api_key(monkeypatch):
    """Test behavior when GOOGLE_API_KEY is not set"""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc:
        executor(**VALID_PAYLOAD)
    assert "GOOGLE_API_KEY environment variable not set" in str(exc.value)

def test_missing_project_id(monkeypatch):
    """Test behavior when PROJECT_ID is not set"""
    monkeypatch.delenv("PROJECT_ID", raising=False)
    with pytest.raises(ValueError) as exc:
        executor(**VALID_PAYLOAD)
    assert "PROJECT_ID environment variable not set" in str(exc.value)

# --- Input Validation Tests --- #
@pytest.mark.parametrize("field,invalid_value", [
    ("base_prompt", ""),
    ("base_prompt", None),
    ("grade_level", ""),
    ("grade_level", None),
    ("subject", ""),
    ("subject", None),
])
def test_validation_error_for_invalid_inputs(field, invalid_value):
    """Test validation errors for various invalid inputs"""
    invalid_payload = {**VALID_PAYLOAD, field: invalid_value}
    with pytest.raises(ValueError) as exc:
        executor(**invalid_payload)
    assert str(exc.value)  # Ensure there's an error message

@patch('app.tools.image_generator.tools.check_prompt_safety')
def test_validation_accepts_none_language(mock_safety_check, mock_image_generator):
    """Test that language can be None"""
    # Mock the safety check to return safe
    mock_safety_check.return_value = (True, "SAFE: The prompt is appropriate")
    
    payload = {**VALID_PAYLOAD, "language": None}
    result = executor(**payload, verbose=False)
    assert isinstance(result, dict)
    assert "image_url" in result

# --- Error Handling Tests --- #
def test_tool_executor_error_wrapped(monkeypatch):
    """Test that errors from executor_image_generator are properly handled"""
    def mock_raise(*args, **kwargs):
        raise ToolExecutorError("Image generation failed")
    
    monkeypatch.setattr(
        "app.tools.image_generator.core.executor_image_generator",
        mock_raise
    )
    
    with pytest.raises(ValueError) as exc:
        executor(**VALID_PAYLOAD)
    assert "Image generation failed" in str(exc.value)

def test_unexpected_error_handling(monkeypatch):
    """Test handling of unexpected errors"""
    def mock_raise(*args, **kwargs):
        raise Exception("Unexpected error")
    
    monkeypatch.setattr(
        "app.tools.image_generator.core.executor_image_generator",
        mock_raise
    )
    
    with pytest.raises(ValueError) as exc:
        executor(**VALID_PAYLOAD)
    assert "Unexpected error" in str(exc.value)

# --- Output Validation Tests --- #
def test_output_validation(mock_image_generator):
    """Test that the output is properly validated"""
    mock_image_generator.return_value = {"image_url": "https://valid.url/image.png"}
    result = executor(**VALID_PAYLOAD)
    assert isinstance(result, dict)
    assert "image_url" in result
    assert isinstance(result["image_url"], str)

def test_invalid_output_structure(mock_image_generator):
    """Test handling of invalid output structure"""
    mock_image_generator.return_value = {"wrong_key": "value"}
    with pytest.raises(ValueError):
        executor(**VALID_PAYLOAD)
