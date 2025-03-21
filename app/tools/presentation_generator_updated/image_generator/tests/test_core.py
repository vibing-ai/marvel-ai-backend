import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from io import BytesIO
from app.tools.presentation_generator_updated.image_generator.tools import ImageGenerator
from app.tools.presentation_generator_updated.image_generator.core import executor
from app.api.error_utilities import LoaderError, ToolExecutorError


# Fixtures for test data
@pytest.fixture
def mock_image_data():
    return "https://storage.googleapis.com/slide-images-bucket/123-test-uuid.png"


@pytest.fixture
def mock_prompt_model():
    """Create a mock for the prompt model (Gemini)."""
    mock_model = MagicMock()
    mock_model.invoke.return_value = "Test generated prompt"
    return mock_model


@pytest.fixture
def mock_image_generator(mock_prompt_model):
    """Create a mock ImageGenerator instance with mocked dependencies."""
    image_generator = ImageGenerator(
        prompt_model=mock_prompt_model,
        image_model="flux"
    )
    # Mock the _construct_image_generation_prompt method
    image_generator._construct_image_generation_prompt = MagicMock(
        return_value="A detailed image showing physics concepts"
    )
    return image_generator


# Test the prompt construction method
def test_construct_image_generation_prompt_string_content(mock_prompt_model):
    """Test prompt construction with string content."""
    image_generator = ImageGenerator(prompt_model=mock_prompt_model)
    
    title = "Introduction to Physics"
    content = "This slide covers the basics of Newtonian mechanics."
    layout = "titleAndBody"
    
    prompt = image_generator._construct_image_generation_prompt(title, content, layout)
    
    # Verify the mock was called with expected arguments
    mock_prompt_model.invoke.assert_called_once()
    # Check if the result matches what we expect
    assert prompt == "Test generated prompt"


def test_construct_image_generation_prompt_list_content(mock_prompt_model):
    """Test prompt construction with list content."""
    image_generator = ImageGenerator(prompt_model=mock_prompt_model)
    
    title = "Key Points"
    content = ["First law of motion", "Second law of motion", "Third law of motion"]
    layout = "titleAndBullets"
    
    prompt = image_generator._construct_image_generation_prompt(title, content, layout)
    
    # Verify the content gets joined correctly
    call_args = mock_prompt_model.invoke.call_args[0][0]
    assert "First law of motion. Second law of motion. Third law of motion" in call_args


def test_construct_image_generation_prompt_dict_content(mock_prompt_model):
    """Test prompt construction with dictionary content (two columns)."""
    image_generator = ImageGenerator(prompt_model=mock_prompt_model)
    
    title = "Compare and Contrast"
    content = {
        "leftColumn": "Benefits of approach A",
        "rightColumn": "Benefits of approach B"
    }
    layout = "twoColumn"
    
    prompt = image_generator._construct_image_generation_prompt(title, content, layout)
    
    # Verify the content from both columns gets included
    call_args = mock_prompt_model.invoke.call_args[0][0]
    assert "Benefits of approach A. Benefits of approach B" in call_args


def test_construct_image_generation_prompt_error_handling(mock_prompt_model):
    """Test error handling when prompt generation fails."""
    image_generator = ImageGenerator(prompt_model=mock_prompt_model)
    
    # Make the mock raise an exception
    mock_prompt_model.invoke.side_effect = Exception("API error")
    
    title = "Error Test"
    content = "Content"
    layout = "blank"
    
    # Verify that the exception is propagated
    with pytest.raises(Exception) as excinfo:
        image_generator._construct_image_generation_prompt(title, content, layout)
    
    assert "Error generating image prompt with Gemini" in str(excinfo.value)


# Test the image generation method with flux model
@patch('replicate.run')
@patch('google.cloud.storage.Client')
@patch('uuid.uuid4')
def test_generate_slide_image_flux(mock_uuid, mock_storage_client, mock_replicate_run, mock_image_generator):
    """Test generate_slide_image with flux model."""
    # Setup mocks
    mock_uuid.return_value = "test-uuid"
    
    # Mock replicate output
    mock_image = MagicMock()
    mock_image.read.return_value = b"fake image content"
    mock_replicate_run.return_value = [mock_image]
    
    # Mock GCS client
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.public_url = "https://storage.googleapis.com/slide-images-bucket/123-test-uuid.png"
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    
    # Call the method
    result = mock_image_generator.generate_slide_image(
        slide_id=123,
        title="Test Title",
        content="Test Content",
        layout="titleAndBody"
    )
    
    # Assertions
    mock_replicate_run.assert_called_once()
    assert result == "https://storage.googleapis.com/slide-images-bucket/123-test-uuid.png"
    mock_bucket.blob.assert_called_once_with("123-test-uuid.png")
    mock_blob.upload_from_file.assert_called_once()
    mock_blob.make_public.assert_called_once()


# Test the image generation method with imagen model
@patch('vertexai.preview.vision_models.ImageGenerationModel.from_pretrained')
@patch('google.cloud.storage.Client')
@patch('uuid.uuid4')
def test_generate_slide_image_imagen(mock_uuid, mock_storage_client, mock_imagen_model, mock_image_generator):
    """Test generate_slide_image with imagen model."""
    # Setup mocks
    mock_uuid.return_value = "test-uuid"
    
    # Change image model to imagen
    mock_image_generator.image_model = "imagen"
    
    # Mock Imagen model
    mock_model = MagicMock()
    mock_imagen_model.return_value = mock_model
    
    # Mock generated image
    mock_image = MagicMock()
    mock_image._pil_image = MagicMock()
    mock_image._pil_image.save = MagicMock()
    mock_model.generate_images.return_value = [mock_image]
    
    # Mock GCS client
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.public_url = "https://storage.googleapis.com/slide-images-bucket/123-test-uuid.png"
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    
    # Call the method
    result = mock_image_generator.generate_slide_image(
        slide_id=123,
        title="Test Title",
        content="Test Content",
        layout="titleAndBody"
    )
    
    # Assertions
    mock_model.generate_images.assert_called_once()
    assert result == "https://storage.googleapis.com/slide-images-bucket/123-test-uuid.png"
    mock_bucket.blob.assert_called_once_with("123-test-uuid.png")
    mock_blob.upload_from_file.assert_called_once()
    mock_blob.make_public.assert_called_once()


# Test the retry mechanism
@patch('replicate.run')
@patch('google.cloud.storage.Client')
@patch('uuid.uuid4')
def test_generate_slide_image_retry(mock_uuid, mock_storage_client, mock_replicate_run, mock_image_generator):
    """Test image generation with retry on failure."""
    # Setup mocks
    mock_uuid.return_value = "test-uuid"
    
    # Mock replicate output
    mock_image = MagicMock()
    mock_image.read.return_value = b"fake image content"
    
    # First call raises exception, second call succeeds
    mock_replicate_run.side_effect = [
        Exception("API error"),
        [mock_image]  # This needs to be a list containing a mock that has .read() method
    ]
    
    # Mock GCS client
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.public_url = "https://storage.googleapis.com/slide-images-bucket/123-test-uuid.png"
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    
    # Call the method
    result = mock_image_generator.generate_slide_image(
        slide_id=123,
        title="Test Title",
        content="Test Content",
        layout="titleAndBody"
    )
    
    # Assertions
    assert mock_replicate_run.call_count == 2
    assert result == "https://storage.googleapis.com/slide-images-bucket/123-test-uuid.png"


# Test fallback to placeholder when all attempts fail
@patch('replicate.run')
def test_generate_slide_image_all_attempts_fail(mock_replicate_run, mock_image_generator):
    """Test fallback to placeholder when all attempts fail."""
    # All calls raise exceptions
    mock_replicate_run.side_effect = Exception("API error")
    
    # Call the method
    result = mock_image_generator.generate_slide_image(
        slide_id=123,
        title="Test Title",
        content="Test Content",
        layout="titleAndBody"
    )
    
    # Assertions
    assert result.startswith("https://via.placeholder.com/")
    assert "Test+Title" in result


# Test the executor function
@patch('app.tools.presentation_generator_updated.image_generator.core.ImageGenerator')
def test_executor_successful(mock_image_generator_class, mock_image_data):
    """Test successful execution of the executor function."""
    # Setup mock
    mock_instance = MagicMock()
    mock_instance.generate_slide_image.return_value = mock_image_data
    mock_image_generator_class.return_value = mock_instance
    
    # Call the executor
    result = executor(
        slide_id=123,
        title="Test Title",
        content="Test Content",
        layout="titleAndBody",
        image_model="flux",
        verbose=True
    )
    
    # Assertions
    mock_image_generator_class.assert_called_once_with(image_model="flux")
    mock_instance.generate_slide_image.assert_called_once_with(
        slide_id=123,
        title="Test Title",
        content="Test Content",
        layout="titleAndBody"
    )
    assert result == mock_image_data


def test_executor_missing_inputs():
    """Test executor with missing required inputs."""
    # Test with missing title
    with pytest.raises(ValueError) as excinfo:
        executor(
            slide_id=123,
            title="",  # Empty title
            content="Test Content",
            layout="titleAndBody"
        )
    assert "Missing required inputs" in str(excinfo.value)
    
    # Test with missing content
    with pytest.raises(ValueError) as excinfo:
        executor(
            slide_id=123,
            title="Test Title",
            content="",  # Empty content
            layout="titleAndBody"
        )
    assert "Missing required inputs" in str(excinfo.value)
    
    # Test with missing layout
    with pytest.raises(ValueError) as excinfo:
        executor(
            slide_id=123,
            title="Test Title",
            content="Test Content",
            layout=""  # Empty layout
        )
    assert "Missing required inputs" in str(excinfo.value)


@patch('app.tools.presentation_generator_updated.image_generator.core.ImageGenerator')
def test_executor_loader_error(mock_image_generator_class):
    """Test executor handling of LoaderError."""
    # Setup mock to raise LoaderError
    mock_instance = MagicMock()
    mock_instance.generate_slide_image.side_effect = LoaderError("Failed to load image model")
    mock_image_generator_class.return_value = mock_instance
    
    # Test that LoaderError is converted to ToolExecutorError
    with pytest.raises(ToolExecutorError) as excinfo:
        executor(
            slide_id=123,
            title="Test Title",
            content="Test Content",
            layout="titleAndBody"
        )
    assert "Failed to load image model" in str(excinfo.value)


@patch('app.tools.presentation_generator_updated.image_generator.core.ImageGenerator')
def test_executor_general_exception(mock_image_generator_class):
    """Test executor handling of general exceptions."""
    # Setup mock to raise a general exception
    mock_instance = MagicMock()
    mock_instance.generate_slide_image.side_effect = Exception("Unexpected error")
    mock_image_generator_class.return_value = mock_instance
    
    # Test that general exceptions are converted to ValueError
    with pytest.raises(ValueError) as excinfo:
        executor(
            slide_id=123,
            title="Test Title",
            content="Test Content",
            layout="titleAndBody"
        )
    assert "Error in image generator executor" in str(excinfo.value)
    assert "Unexpected error" in str(excinfo.value)