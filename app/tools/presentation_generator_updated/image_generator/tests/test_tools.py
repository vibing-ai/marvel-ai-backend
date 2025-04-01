import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import base64
import json
from app.tools.presentation_generator_updated.image_generator.tools import (
    ImageGenerator, ImagePromptGenerator, ThemeOutput, VisualPromptOutput,
    save_to_file, image_generation_handler
)

# Fixtures
@pytest.fixture
def mock_bucket():
    return Mock()

@pytest.fixture
def image_generator(mock_bucket):
    generator = ImageGenerator()
    generator.bucket = mock_bucket
    return generator

@pytest.fixture
def sample_slides_data():
    return [
        {
            "title": "Introduction to AI",
            "content": "Overview of artificial intelligence",
            "template": "title"
        },
        {
            "title": "Machine Learning Basics",
            "content": ["Supervised Learning", "Unsupervised Learning"],
            "template": "twoColumn"
        }
    ]

@pytest.fixture
def mock_genai_model():
    mock_model = Mock()
    mock_model.invoke = Mock(return_value={"theme": "Modern Technology"})
    return mock_model

@pytest.fixture
def mock_together_client():
    with patch('together.Together') as mock_together:
        mock_client = Mock()
        mock_client.images = Mock()
        mock_client.images.generate.return_value = Mock(
            data=[Mock(b64_json="fake_base64_data")]
        )
        mock_together.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_storage_client():
    with patch('google.cloud.storage.Client') as mock_storage:
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.public_url = "https://storage.url/test.png"
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_client
        yield mock_client

# Tests for ImageGenerator
def test_image_generator_initialization():
    generator = ImageGenerator()
    assert generator is not None
    assert hasattr(generator, 'bucket')

def test_generate_single_image_success(image_generator):
    # Mock successful image generation
    image_generator._generate_image = Mock(return_value="base64_image_data")
    image_generator._save_image_to_gcs = Mock(return_value="https://storage.url/image.png")
    
    result = image_generator.generate_single_image({
        "prompt": "test prompt",
        "title": "Test Title"
    })
    
    assert result["status"] == "success"
    assert result["image_url"] == "https://storage.url/image.png"
    assert result["title"] == "Test Title"

def test_generate_single_image_failure(image_generator):
    # Mock the Together client's generate method to raise an exception
    with patch.object(image_generator.client.images, 'generate', side_effect=Exception("API Error")):
        result = image_generator.generate_single_image({
            "prompt": "test prompt",
            "title": "Test Title"
        })
        
        assert result["status"] == "failed"
        assert "error" in result
        assert result["title"] == "Test Title"

def test_save_image_to_gcs(image_generator, mock_bucket):
    # Mock successful GCS upload
    mock_blob = Mock()
    mock_blob.public_url = "https://storage.url/image.png"
    mock_bucket.blob.return_value = mock_blob
    
    image_data = base64.b64encode(b"fake_image_data").decode()
    result = image_generator._save_image_to_gcs(image_data, "Test Title")
    
    assert result == "https://storage.url/image.png"
    mock_bucket.blob.assert_called_once()
    mock_blob.upload_from_string.assert_called_once()

# Tests for ImagePromptGenerator
def test_image_prompt_generator_initialization():
    with patch('app.tools.presentation_generator_updated.image_generator.tools.read_text_file') as mock_read:
        mock_read.return_value = "test prompt"
        generator = ImagePromptGenerator()
        assert generator.prompt == "test prompt"

def test_generate_image_prompt(mock_genai_model):
    """
    Test that ImagePromptGenerator correctly generates image prompts from slides data.
    """
    # Setup
    test_prompt_template = "test prompt"
    test_slides = [{
        "title": "Test Slide",
        "content": "Test Content",
        "template": "default"
    }]

    # Mock the template file reading
    with patch('app.tools.presentation_generator_updated.image_generator.tools.read_text_file') as mock_read:
        mock_read.return_value = test_prompt_template
        
        # Configure mock model responses
        mock_genai_model.invoke.side_effect = [
            # First call for theme generation
            ThemeOutput(theme="A modern technological theme").model_dump_json(),
            # Second call for visual prompt generation
            VisualPromptOutput(
                visual_description="A detailed visual description for the slide"
            ).model_dump_json()
        ]

        # Execute
        generator = ImagePromptGenerator()
        generator.model = mock_genai_model
        result = generator.generate_image_prompt(test_slides)

        # Assert
        assert mock_genai_model.invoke.call_count == 2, "Model should be called twice - for theme and visual"
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "Test Slide" in result, "Result should contain the slide title as key"
        assert isinstance(result["Test Slide"], str), "Generated prompt should be a string"
        
        # Verify mock was called with correct template
        mock_read.assert_called_once()


def test_generate_image_prompt_empty_slides():
    generator = ImagePromptGenerator()
    with pytest.raises(ValueError, match="Slides data cannot be empty"):
        generator.generate_image_prompt([])

# Tests for image_generation_handler
def test_image_generation_handler_success():
    mock_args = Mock()
    mock_args.presentation_content = [{"title": "Test Slide", "content": "Test Content"}]
    
    with patch('app.tools.presentation_generator_updated.image_generator.tools.ImagePromptGenerator') as mock_prompt_gen:
        mock_prompt_gen.return_value.generate_image_prompt.return_value = {"Test Slide": "test prompt"}
        
        with patch('app.tools.presentation_generator_updated.image_generator.tools.create_image_generation_chain') as mock_chain:
            mock_chain.return_value.invoke.return_value = {
                "image_0": {
                    "status": "success",
                    "title": "Test Slide",
                    "image_url": "https://example.com/image.png"
                }
            }
            
            result = image_generation_handler(mock_args)
            
            assert result["status"] == "success"
            assert isinstance(result["data"], dict)

def test_image_generation_handler_error():
    mock_args = Mock()
    mock_args.presentation_content = []
    
    result = image_generation_handler(mock_args)
    assert result["status"] == "error"
    assert "message" in result

# Tests for save_to_file
def test_save_to_file(tmp_path):
    with patch('os.path.dirname') as mock_dirname:
        mock_dirname.return_value = str(tmp_path)
        data = {"test": "data"}
        save_to_file(data, "test.json")
        
        output_dir = tmp_path / "generated_prompts"
        assert output_dir.exists()
        assert (output_dir / "test.json").exists()

def test_save_to_file_error():
    with patch('os.path.dirname', side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            save_to_file({"test": "data"}, "test.json")











