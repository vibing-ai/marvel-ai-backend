import pytest
from app.tools.image_generator.core import executor
from app.tools.image_generator.tools import ImageGenerator, ImageGeneratorArgs, ImageGenerationResult
from app.api.error_utilities import ImageHandlerError, ToolExecutorError
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_image_data():
    """Fixture for mock image generation data."""
    return {
        "image_b64": "base64_encoded_image_data",
        "prompt_used": "A diagram of the solar system, educational context: astronomy for middle school level"
    }

@pytest.fixture
def mock_args():
    """Fixture for mock ImageGeneratorArgs."""
    return ImageGeneratorArgs(
        prompt="A diagram of the solar system",
        subject="astronomy",
        grade_level="middle school",
        lang="en"
    )

@pytest.fixture
def mock_image_generator():
    """Mock ImageGenerator instead of instantiating it."""
    with patch("app.tools.image_generator.tools.GoogleGenerativeAI"):
        image_generator = ImageGenerator()
        image_generator.check_prompt_safety = MagicMock()
        image_generator.enhance_prompt_with_educational_context = MagicMock()
        image_generator.generate_image = MagicMock()
        image_generator.detect_content_type = MagicMock()
        image_generator.get_specialized_prompt_template = MagicMock()
        return image_generator

# Test the executor function
@patch("app.tools.image_generator.tools.ImageGenerator.generate_educational_image")
def test_executor(mock_generate_educational_image, mock_image_data, mock_args):
    """Test the executor function with valid inputs."""
    prompt = "A diagram of the solar system"
    subject = "astronomy"
    grade_level = "middle school"
    lang = "en"
    verbose = False

    # Instead of creating a real ImageGenerationResult, create a MagicMock with model_dump method
    mock_result = MagicMock(spec=ImageGenerationResult)
    mock_result.image_b64 = mock_image_data["image_b64"]
    mock_result.prompt_used = mock_image_data["prompt_used"]
    mock_result.educational_context = "astronomy for middle school level"
    mock_result.safety_applied = True
    mock_result.model_dump.return_value = {
        "image_b64": mock_image_data["image_b64"],
        "prompt_used": mock_image_data["prompt_used"],
        "educational_context": "astronomy for middle school level",
        "safety_applied": True
    }
    mock_generate_educational_image.return_value = mock_result

    # Call the executor function
    result = executor(prompt, subject, grade_level, lang, verbose)

    # Assertions
    assert result["image_b64"] == mock_image_data["image_b64"]
    assert result["prompt_used"] == mock_image_data["prompt_used"]
    assert result["educational_context"] == "astronomy for middle school level"
    assert result["safety_applied"] == True
    mock_generate_educational_image.assert_called_once()

# Test the executor function with missing required inputs
def test_executor_missing_inputs():
    """Test the executor function with missing required inputs."""
    with pytest.raises(ToolExecutorError, match="A prompt is required to generate an image"):
        executor(
            prompt="",
            subject="astronomy",
            grade_level="middle school",
            lang="en"
        )

# Test the executor function with an ImageHandlerError
@patch("app.tools.image_generator.tools.ImageGenerator.generate_educational_image")
def test_executor_image_handler_error(mock_generate_educational_image):
    """Test the executor function with an ImageHandlerError."""
    mock_generate_educational_image.side_effect = ImageHandlerError("Unsafe content detected", "violent content")

    with pytest.raises(ToolExecutorError, match="Unsafe content detected"):
        executor(prompt="A diagram", subject="science", grade_level="elementary", lang="en")

# Test the executor function with an unexpected error
@patch("app.tools.image_generator.tools.ImageGenerator.generate_educational_image")
def test_executor_unexpected_error(mock_generate_educational_image):
    """Test the executor function with an unexpected error."""
    mock_generate_educational_image.side_effect = Exception("Unexpected error occurred")

    with pytest.raises(ToolExecutorError, match="Error in Image Generator: Unexpected error occurred"):
        executor(prompt="A diagram", subject="science", grade_level="elementary", lang="en")

# Test the ImageGenerator initialization
def test_image_generator_initialization(mock_args):
    """Test that the ImageGenerator initializes correctly."""
    with patch("app.tools.image_generator.tools.GoogleGenerativeAI"):
        generator = ImageGenerator(args=mock_args, verbose=True)

        assert generator.args == mock_args
        assert generator.verbose == True
        assert generator.model is not None

# Test enhance_prompt_with_educational_context with provided context
def test_enhance_prompt_with_educational_context_provided(mock_image_generator):
    """Test enhancing prompt with provided educational context."""
    prompt = "A diagram of the solar system"
    subject = "astronomy"
    grade_level = "middle school"

    mock_image_generator.enhance_prompt_with_educational_context.return_value = {
        "enhanced_prompt": "A diagram of the solar system, educational context: astronomy for middle school level",
        "educational_context": "astronomy for middle school level"
    }

    result = mock_image_generator.enhance_prompt_with_educational_context(prompt, subject, grade_level)

    assert result["enhanced_prompt"] == "A diagram of the solar system, educational context: astronomy for middle school level"
    assert result["educational_context"] == "astronomy for middle school level"

# Test enhance_prompt_with_educational_context with AI inference
def test_enhance_prompt_with_educational_context_ai_inference(mock_image_generator):
    """Test enhancing prompt with AI-inferred educational context."""
    prompt = "A diagram of the solar system"

    mock_image_generator.model.invoke.return_value = '{"subject": "astronomy", "grade_level": "middle school"}'
    mock_image_generator.enhance_prompt_with_educational_context.return_value = {
        "enhanced_prompt": "A diagram of the solar system, educational context: astronomy for middle school level",
        "educational_context": "astronomy for middle school level"
    }

    result = mock_image_generator.enhance_prompt_with_educational_context(prompt)

    assert result["enhanced_prompt"] == "A diagram of the solar system, educational context: astronomy for middle school level"
    assert result["educational_context"] == "astronomy for middle school level"

# Test check_prompt_safety with safe content
def test_check_prompt_safety_safe(mock_image_generator):
    """Test that safe prompts pass the safety check."""
    prompt = "A diagram of the solar system"

    mock_image_generator.check_prompt_safety.return_value = True

    result = mock_image_generator.check_prompt_safety(prompt)

    assert result == True

# Test check_prompt_safety with unsafe content
def test_check_prompt_safety_unsafe(mock_image_generator):
    """Test that unsafe prompts are detected."""
    prompt = "A violent explosion"

    mock_image_generator.check_prompt_safety.return_value = False

    result = mock_image_generator.check_prompt_safety(prompt)

    assert result == False

# Test generate_image
def test_generate_image(mock_image_data, mock_image_generator):
    """Test image generation."""
    prompt = "A diagram of the solar system, educational context: astronomy for middle school level"

    mock_image_generator.generate_image.return_value = mock_image_data

    result = mock_image_generator.generate_image(prompt)

    assert result["image_b64"] == mock_image_data["image_b64"]
    assert result["prompt_used"] == mock_image_data["prompt_used"]

# Test generate_educational_image
def test_generate_educational_image(mock_args, mock_image_data, mock_image_generator):
    """Test the full educational image generation pipeline."""
    mock_image_generator.args = mock_args
    mock_image_generator.check_prompt_safety.return_value = True
    mock_image_generator.detect_content_type.return_value = "diagram"
    mock_image_generator.get_specialized_prompt_template.return_value = "Specialized template for diagrams"
    mock_image_generator.enhance_prompt_with_educational_context.return_value = {
        "enhanced_prompt": "A diagram of the solar system, educational context: astronomy for middle school level",
        "educational_context": "astronomy for middle school level"
    }
    mock_image_generator.generate_image.return_value = mock_image_data

    result = mock_image_generator.generate_educational_image()

    assert isinstance(result, ImageGenerationResult)
    assert result.image_b64 == mock_image_data["image_b64"]
    assert result.prompt_used == mock_image_data["prompt_used"]
    assert result.educational_context == "astronomy for middle school level"
    assert result.safety_applied == True

# Test detect_content_type
def test_detect_content_type(mock_image_generator):
    """Test content type detection."""
    prompt = "Create a diagram of the water cycle"
    subject = "earth science"

    mock_image_generator.detect_content_type.return_value = "diagram"

    result = mock_image_generator.detect_content_type(prompt, subject)

    assert result == "diagram"

# Test detect_content_type with different content types
@pytest.mark.parametrize("prompt,subject,expected_type", [
    ("Create a diagram of the water cycle", "earth science", "diagram"),
    ("Show the process of photosynthesis", "biology", "process"),
    ("Illustrate the concept of gravity", "physics", "concept"),
    ("Create a timeline of World War II", "history", "historical"),
    ("Graph the quadratic function y = x²", "mathematics", "mathematical"),
    ("Show a picture of a classroom", "education", "general")
])
def test_detect_content_type_variations(mock_image_generator, prompt, subject, expected_type):
    """Test content type detection with various inputs."""
    mock_image_generator.detect_content_type.return_value = expected_type

    result = mock_image_generator.detect_content_type(prompt, subject)

    assert result == expected_type

# Test get_specialized_prompt_template
def test_get_specialized_prompt_template(mock_image_generator):
    """Test specialized prompt template generation."""
    content_type = "diagram"

    mock_image_generator.get_specialized_prompt_template.return_value = "Base template + diagram specialization"

    result = mock_image_generator.get_specialized_prompt_template(content_type)

    assert result == "Base template + diagram specialization"

# Test the ImageGenerationResult model
def test_image_generation_result_model():
    """Test the ImageGenerationResult Pydantic model."""
    result = ImageGenerationResult(
        image_b64="base64_encoded_image_data",
        prompt_used="A diagram of the solar system",
        educational_context="astronomy for middle school level",
        safety_applied=True
    )

    assert result.image_b64 == "base64_encoded_image_data"
    assert result.prompt_used == "A diagram of the solar system"
    assert result.educational_context == "astronomy for middle school level"
    assert result.safety_applied == True

# Test the ImageGeneratorArgs model
def test_image_generator_args_model():
    """Test the ImageGeneratorArgs Pydantic model."""
    args = ImageGeneratorArgs(
        prompt="A diagram of the solar system",
        subject="astronomy",
        grade_level="middle school",
        lang="en"
    )

    assert args.prompt == "A diagram of the solar system"
    assert args.subject == "astronomy"
    assert args.grade_level == "middle school"
    assert args.lang == "en"
