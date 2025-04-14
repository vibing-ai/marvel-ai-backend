import pytest
from unittest.mock import patch, MagicMock, Mock
from app.tools.image_generator.core import executor, ImageGeneratorArgs
from app.tools.image_generator.tool import ImageGenerator, ImageGenerationOutput, SafetyCheckOutput

@pytest.fixture
def base_input():
    return {
        "prompt": "A scientific diagram of photosynthesis",
        "subject": "Biology",
        "grade_level": "High School",
        "presets": {"style": "educational"},
        "lang": "en"
    }

@pytest.fixture
def mock_args():
    return ImageGeneratorArgs(
        prompt="Test prompt",
        subject="Science",
        grade_level="High School",
        presets={"style": "educational"},
        lang="en"
    )

@pytest.fixture
def mock_image_generator():
    return MagicMock(spec=ImageGenerator)

def test_executor_normal_operation(base_input, mock_image_generator):
    """Test successful image generation."""
    expected_output = {
        "image_url": "https://example.com/image.png",
        "enhanced_prompt": "Enhanced test prompt"
    }
    
    mock_image_generator.generate_image.return_value = expected_output
    
    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        result = executor(**base_input)
    
    assert result == expected_output
    mock_image_generator.generate_image.assert_called_once()

def test_executor_safety_error(base_input, mock_image_generator):
    """Test executor handling safety check failure."""
    error_message = "Content safety check failed - prompt contains inappropriate content"
    mock_image_generator.generate_image.return_value = {"error": error_message}
    
    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        result = executor(**base_input)
    
    assert "error" in result
    assert result["error"] == error_message

def test_executor_missing_inputs():
    """Test executor with missing required inputs."""
    with pytest.raises(ValueError):
        executor(prompt="", subject=None, grade_level=None, lang="en")

def test_executor_unexpected_error(base_input, mock_image_generator):
    """Test executor handling unexpected errors."""
    mock_image_generator.generate_image.side_effect = Exception("Unexpected error")
    
    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        result = executor(**base_input)
    
    assert "error" in result
    assert "Unexpected error" in result["error"]