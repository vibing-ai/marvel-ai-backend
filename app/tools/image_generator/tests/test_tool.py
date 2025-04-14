import pytest
from unittest.mock import patch, MagicMock, Mock
from app.tools.image_generator.tool import ImageGenerator, ImageGenerationOutput, SafetyCheckOutput
import io
from PIL import Image

@pytest.fixture
def mock_vertex_response():
    mock_image = MagicMock()
    mock_image._image_bytes = b"fake_image_data"
    mock_response = MagicMock()
    mock_response.images = [mock_image]
    return mock_response

@pytest.fixture
def image_generator(mock_args):
    return ImageGenerator(args=mock_args)

def test_enhance_prompt(image_generator):
    """Test prompt enhancement functionality."""
    enhanced_output = ImageGenerationOutput(
        image_prompt="Enhanced educational prompt for photosynthesis diagram"
    )
    
    with patch.object(image_generator, 'model') as mock_model:
        mock_model.invoke.return_value = enhanced_output
        result = image_generator.enhance_prompt()
    
    assert isinstance(result, ImageGenerationOutput)
    assert "Enhanced" in result.image_prompt

def test_safety_check_pass(image_generator):
    """Test safety check with safe content."""
    safe_prompt = "Educational diagram of cell structure"
    
    with patch.object(image_generator, 'model') as mock_model:
        mock_model.invoke.return_value = SafetyCheckOutput(
            is_safe=True,
            details={"educational_value": True}
        )
        result = image_generator.safety_check(safe_prompt)
    
    assert result is True

def test_safety_check_fail(image_generator):
    """Test safety check with unsafe content."""
    unsafe_prompt = "violent content"
    
    with patch.object(image_generator, 'model') as mock_model:
        mock_model.invoke.return_value = SafetyCheckOutput(
            is_safe=False,
            details={"reason": "Contains inappropriate content"}
        )
        result = image_generator.safety_check(unsafe_prompt)
    
    assert result is False

@patch("vertexai.preview.vision_models.ImageGenerationModel")
def test_generate_image_success(mock_imagen_model, image_generator, mock_vertex_response):
    """Test successful image generation."""
    mock_model = MagicMock()
    mock_model.generate_images.return_value = mock_vertex_response
    mock_imagen_model.from_pretrained.return_value = mock_model
    
    # Mock Firebase upload
    with patch("app.tools.presentation_generator_updated.slide_generator.firebase.FirebaseManager") as mock_firebase:
        mock_firebase.return_value.upload_image.return_value = "https://example.com/image.png"
        
        result = image_generator.generate_image()
    
    assert "image_url" in result
    assert "enhanced_prompt" in result
    assert result["image_url"] == "https://example.com/image.png"

def test_generate_image_safety_fail(image_generator):
    """Test image generation with safety check failure."""
    with patch.object(image_generator, 'safety_check', return_value=False):
        result = image_generator.generate_image()
    
    assert "error" in result
    assert "safety check failed" in result["error"].lower()

def test_generate_image_vertex_error(image_generator):
    """Test handling of Vertex AI API errors."""
    with patch.object(image_generator, 'safety_check', return_value=True):
        with patch.object(image_generator, 'image_generator_model') as mock_model:
            mock_model.generate_images.side_effect = Exception("API Error")
            result = image_generator.generate_image()
    
    assert "error" in result
    assert "Image generation failed" in result["error"]

def test_firebase_upload_failure(image_generator, mock_vertex_response):
    """Test handling of Firebase upload failures."""
    with patch.object(image_generator, 'safety_check', return_value=True):
        with patch.object(image_generator, 'image_generator_model') as mock_model:
            mock_model.generate_images.return_value = mock_vertex_response
            with patch("app.tools.presentation_generator_updated.slide_generator.firebase.FirebaseManager") as mock_firebase:
                mock_firebase.return_value.upload_image.return_value = None
                result = image_generator.generate_image()
    
    assert "error" in result
    assert "Failed to upload" in result["error"]

def test_image_generation_output_model():
    """Test ImageGenerationOutput Pydantic model."""
    output = ImageGenerationOutput(
        image_prompt="Test prompt"
    )
    assert output.image_prompt == "Test prompt"

def test_safety_check_output_model():
    """Test SafetyCheckOutput Pydantic model."""
    output = SafetyCheckOutput(
        is_safe=True,
        details={"reason": "Content is appropriate"}
    )
    assert output.is_safe is True
    assert "reason" in output.details