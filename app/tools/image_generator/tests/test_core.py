import pytest
from unittest.mock import patch, MagicMock
from app.tools.image_generator.core import executor
from app.tools.image_generator.tool import ImageGenerator, ImageGenerationError
from app.services.schemas import ImageGeneratorArgs
import firebase_admin

@pytest.fixture
def mock_firebase_credentials():
    """Mock Firebase credentials and initialization"""
    mock_cred = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    # Configure mock blob
    mock_blob.public_url = "https://example.com/image.png"
    mock_blob.upload_from_string = MagicMock()
    mock_blob.make_public = MagicMock()
    
    # Configure mock bucket
    mock_bucket.blob = MagicMock(return_value=mock_blob)
    
    with patch('firebase_admin.credentials.Certificate', return_value=mock_cred), \
         patch('firebase_admin.initialize_app'), \
         patch('firebase_admin.storage.bucket', return_value=mock_bucket), \
         patch.dict('os.environ', {
             'GOOGLE_APPLICATION_CREDENTIALS': 'fake/path/to/credentials.json',
             'FIREBASE_STORAGE_BUCKET': 'fake-bucket-name'
         }):
        yield mock_bucket

@pytest.fixture
def mock_image_generator(mock_firebase_credentials):
    """Mock ImageGenerator instead of instantiating it."""
    with patch("app.tools.image_generator.tool.GoogleGenerativeAI"), \
         patch("app.tools.image_generator.tool.ImageGenerationModel") as mock_imagen, \
         patch("app.tools.image_generator.tool.JsonOutputParser") :
        
        # Set up mock image generation response
        mock_image = MagicMock()
        mock_image._image_bytes = b"fake_image_data"
        mock_response = MagicMock()
        mock_response.images = [mock_image]
        
        # Setup mock model
        mock_model = MagicMock()
        mock_model.generate_images.return_value = mock_response
        mock_imagen.from_pretrained.return_value = mock_model

        # Reset Firebase app if already initialized
        if firebase_admin._apps:
            firebase_admin._apps.clear()
            
        image_generator = ImageGenerator(
            args=ImageGeneratorArgs(
                prompt="test prompt",
                subject="test subject",
                grade_level="test grade",
                presets=None,
                lang="en"
            )
        )
        
        # Mock the enhance_prompt method
        image_generator.enhance_prompt = MagicMock(return_value={
            "image_prompt": "Enhanced test prompt",
            "is_safe": True
        })
        
        # Mock the safety_check method
        image_generator.safety_check = MagicMock(return_value={
            "is_safe": True,
            "details": {
                "detected_keywords": [],
                "severity_score": 1,
                "educational_appropriateness_score": 5,
                "safety_assessment": "Safe and Appropriate",
                "assessment_explanation": "Content is safe and educational"
            }
        })

        return image_generator
#test successful generation of an image
def test_image_generation(mock_image_generator):
    """Test image generation with mocked dependencies."""
    result = mock_image_generator.generate_image()
    print("result:",result)   
    assert "image_url" in result
    assert "enhanced_prompt" in result
    assert result["image_url"] == "https://example.com/image.png"
    assert mock_image_generator.enhance_prompt.called
    assert mock_image_generator.safety_check.called

# test handling of unsafe content
def test_safety_check_failure(mock_image_generator):
    """Test handling of unsafe content."""
    mock_image_generator.safety_check.return_value = {
        "is_safe": False,
        "details": {
            "assessment_explanation": "Unsafe content detected"
        }
    }    
    result = mock_image_generator.generate_image()
    print(result)
    assert "error" in result
    assert "details" in result
    assert "Content safety check failed - prompt contains inappropriate content" in result["error"]

def test_enhance_prompt_failure(mock_image_generator):
    """Test handling of prompt enhancement failure."""
    mock_image_generator.enhance_prompt.return_value = {
        "is_safe": False,
        "image_prompt": "Unsafe prompt detected"
    }
    
    result = mock_image_generator.generate_image()
    print(result)
    assert "error" in result
    assert result.get("is_safe") is False

def test_executor_integration(mock_image_generator):
    """Test integration with executor function."""
    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        result = executor(
            prompt="test prompt",
            subject="test subject",
            grade_level="test grade",
            presets=None,
            lang="en"
        )
        
        assert "image_url" in result
        assert "enhanced_prompt" in result
        assert result["image_url"] == "https://example.com/image.png"


def test_image_generation_model_failure(mock_image_generator):
    """Test handling of image generation model failure."""
    # Configure only the image generation to fail
    mock_image_generator.image_generator_model.generate_images = MagicMock(
        side_effect=Exception("Model error")
    )

    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        with pytest.raises(ImageGenerationError) as exc_info:
            executor(
                prompt="test prompt",
                subject="test subject",
                grade_level="test grade",
                presets=None,
                lang="en"
            )
        print(exc_info.value)
        assert "Image generation failed" in str(exc_info.value)
        # Verify the generate_images method was called
        mock_image_generator.image_generator_model.generate_images.assert_called_once()

def test_cloud_storage_failure(mock_image_generator):
    """Test handling of cloud storage failure."""
    mock_image_generator.save_to_cloud_storage = MagicMock(
        side_effect=Exception("Storage error")
    )
    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        with pytest.raises(ImageGenerationError) as exc_info:
            executor(
                prompt="test prompt",
                subject="test subject",
                grade_level="test grade",
                presets=None,
                lang="en"
            )
    assert "Image generation failed" in str(exc_info.value)
    assert "Storage error" in str(exc_info.value)
        # Verify that save_to_cloud_storage was called
    mock_image_generator.save_to_cloud_storage.assert_called_once()


from app.api.error_utilities import ImageGenerationError

def test_image_generation_error(mock_image_generator):
    """Test handling of ImageGenerationError during image generation."""
    # Configure the image generation to fail with ImageGenerationError
    mock_image_generator.image_generator_model.generate_images = MagicMock(
        return_value=MagicMock(images=[])  # Return empty images list to trigger ImageGenerationError
    )

    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        with pytest.raises(ImageGenerationError) as exc_info:
            executor(
                prompt="test prompt",
                subject="test subject",
                grade_level="test grade",
                presets=None,
                lang="en"
            )
        print(exc_info.value)
        
        assert "No images were generated" in str(exc_info.value)
        # Verify the generate_images method was called
        mock_image_generator.image_generator_model.generate_images.assert_called_once()

def test_image_generation_api_error(mock_image_generator):
    """Test handling of API errors that should raise ImageGenerationError."""
    # Configure the image generation to fail with an API error
    mock_image_generator.image_generator_model.generate_images = MagicMock(
        side_effect=ImageGenerationError("API error occurred")
    )

    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        with pytest.raises(ImageGenerationError) as exc_info:
            executor(
                prompt="test prompt",
                subject="test subject",
                grade_level="test grade",
                presets=None,
                lang="en"
            )
        print(exc_info.value)
        assert "API error occurred" in str(exc_info.value)
        # Verify the generate_images method was called
        mock_image_generator.image_generator_model.generate_images.assert_called_once()

def test_enhance_prompt_value_error(mock_image_generator):
    """Test ValueError handling in enhance_prompt method."""
    # Configure enhance_prompt to raise ValueError
    mock_image_generator.enhance_prompt = MagicMock(
        side_effect=ValueError("Failed to enhance prompt")
    )

    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        with pytest.raises(ValueError) as exc_info:
            executor(
                prompt="test prompt",
                subject="test subject",
                grade_level="test grade",
                presets=None,
                lang="en"
            )
        print(exc_info.value)
        
        assert "Failed to enhance prompt" in str(exc_info.value)
        # Verify enhance_prompt was called
        mock_image_generator.enhance_prompt.assert_called_once()
        # Verify safety_check was not called (since enhance_prompt failed)
        mock_image_generator.safety_check.assert_not_called()

def test_safety_check_value_error(mock_image_generator):
    """Test ValueError handling in safety_check method."""
    # Configure enhance_prompt to return valid data
    mock_image_generator.enhance_prompt.return_value = {
        "image_prompt": "Enhanced test prompt",
        "is_safe": True
    }
    
    # Configure safety_check to raise ValueError
    mock_image_generator.safety_check = MagicMock(
        side_effect=ValueError("Invalid safety check parameters")
    )

    with patch("app.tools.image_generator.core.ImageGenerator", return_value=mock_image_generator):
        with pytest.raises(ValueError) as exc_info:
            executor(
                prompt="test prompt",
                subject="test subject",
                grade_level="test grade",
                presets=None,
                lang="en"
            )
        
        assert "Invalid safety check parameters" in str(exc_info.value)
        # Verify both methods were called in order
        mock_image_generator.enhance_prompt.assert_called_once()
        mock_image_generator.safety_check.assert_called_once()
        # Verify generate_images was not called (since safety_check failed)
        mock_image_generator.image_generator_model.generate_images.assert_not_called()