import pytest
from app.tools.presentation_generator_updated.slide_generator.core import executor, SlideGeneratorInput
from app.tools.presentation_generator_updated.slide_generator.tools import SlideGenerator, Slide, SlidePresentation
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_slide_data():
    return {
        "slides": [
            {
                "title": "Introduction to Python",
                "template": "titleAndBullets",
                "content": ["Python is a programming language"],
                "image_url": "https://storage.googleapis.com/test/intro.jpg"
            },
            {
                "title": "Basic Syntax",
                "template": "twoColumn",
                "content": {"left": "Simple", "right": "Readable"},
                "image_url": "https://storage.googleapis.com/test/syntax.jpg"
            }
        ]
    }

@pytest.fixture
def mock_args():
    return SlideGeneratorInput(
        slides_titles=["Intro", "Details"],
        topic="Data Science",
        instructional_level="Intermediate",
        lang="en"
    )

@pytest.fixture
def mock_slide_generator():
    with patch("app.tools.presentation_generator_updated.slide_generator.tools.GoogleGenerativeAI"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.GoogleGenerativeAIEmbeddings"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.Chroma"):
        slide_generator = SlideGenerator()
        slide_generator.validate_slides_content = MagicMock()
        slide_generator.generate_slides = MagicMock()
        return slide_generator

# Test executor with successful slide generation
def test_executor(mock_slide_data, mock_slide_generator):
    slides_titles = ["Introduction to Python", "Basic Syntax"]
    topic = "Python Programming"
    instructional_level = "Beginner"
    lang = "en"
    verbose = False

    mock_slide_generator.generate_slides.return_value = mock_slide_data
    with patch("app.tools.presentation_generator_updated.slide_generator.core.SlideGenerator", return_value=mock_slide_generator):
        result = executor(slides_titles, topic, instructional_level, lang, verbose)

    assert result == mock_slide_data
    assert all("image_url" in slide for slide in result["slides"])
    mock_slide_generator.generate_slides.assert_called_once()

# Test executor with missing inputs
def test_executor_missing_inputs():
    with pytest.raises(ValueError, match="Missing required inputs"):
        executor(slides_titles=[], topic="", instructional_level="", lang="en")

# Test executor with LoaderError
@patch("app.tools.presentation_generator_updated.slide_generator.tools.SlideGenerator.generate_slides")
def test_executor_loader_error(mock_generate_slides):
    from app.api.error_utilities import LoaderError
    mock_generate_slides.side_effect = LoaderError("Error in Slide Generator Pipeline")
    with pytest.raises(Exception) as exc_info:
        executor(slides_titles=["Intro"], topic="AI", instructional_level="Intermediate", lang="en")
    assert "Error in Slide Generator Pipeline" in str(exc_info.value)

# Test executor with unexpected error
@patch("app.tools.presentation_generator_updated.slide_generator.tools.SlideGenerator.generate_slides")
def test_executor_unexpected_error(mock_generate_slides):
    mock_generate_slides.side_effect = Exception("Unexpected error occurred")
    with pytest.raises(ValueError, match="Error in executor: Unexpected error occurred"):
        executor(slides_titles=["Intro"], topic="AI", instructional_level="Intermediate", lang="en")

# Test validate_slides_content with valid response
def test_validate_slides_content(mock_slide_generator):
    mock_slide_generator.validate_slides_content.return_value = {
        "topic_coverage": 80,
        "template_requirements_met": True,
        "garbage_coverage_percentage": 0,
        "valid": True
    }
    topic = "AI in Education"
    response = {
        "slides": [
            {"title": "AI Intro", "template": "twoColumn", "content": ["AI and learning"], "image_url": "test.jpg"}
        ]
    }
    result = mock_slide_generator.validate_slides_content(response, topic)
    assert result["valid"] == True
    assert result["topic_coverage"] == 80

# Test validate_slides_content with garbage content
def test_validate_slides_content_with_garbage(mock_slide_generator):
    topic = "Introduction"
    response = {
        "slides": [
            {
                "title": "Introduction",
                "template": "sectionHeader",
                "content": ["Unrelated content", "* This should not be here"],
                "image_url": "test.jpg"
            }
        ]
    }
    mock_slide_generator.validate_slides_content.return_value = {
        "topic_coverage": 20,
        "template_requirements_met": False,
        "garbage_coverage_percentage": 50,
        "valid": False
    }
    result = mock_slide_generator.validate_slides_content(response, topic)
    assert result["valid"] == False
    assert result["garbage_coverage_percentage"] == 50

# Test validate_slides_content with empty slides
def test_validate_slides_content_empty_slides(mock_slide_generator):
    topic = "Introduction"
    response = {"slides": []}
    mock_slide_generator.validate_slides_content.side_effect = ValueError("No slides found in the response")
    with pytest.raises(ValueError, match="No slides found in the response"):
        mock_slide_generator.validate_slides_content(response, topic)

# Test compile_context
def test_slide_generator_compile_context(mock_args, mock_slide_generator):
    mock_slide_generator.args = mock_args
    chain = mock_slide_generator.compile_context()
    assert chain is not None

# Test Slide model with image_url
def test_slide_model():
    slide = Slide(
        title="Introduction",
        template="titleAndBullets",
        content=["Key Point 1", "Key Point 2"],
        image_url="https://storage.googleapis.com/test/slide.jpg"
    )
    assert slide.title == "Introduction"
    assert slide.template == "titleAndBullets"
    assert slide.content == ["Key Point 1", "Key Point 2"]
    assert slide.image_url == "https://storage.googleapis.com/test/slide.jpg"

# Test SlidePresentation model
def test_slide_presentation_model():
    slides = [
        Slide(title="Intro", template="titleAndBody", content="Overview", image_url="test1.jpg"),
        Slide(title="Details", template="twoColumn", content={"left": "Content1", "right": "Content2"}, image_url="test2.jpg")
    ]
    presentation = SlidePresentation(slides=slides)
    assert len(presentation.slides) == 2
    assert all(isinstance(slide, Slide) for slide in presentation.slides)
    assert all(slide.image_url is not None for slide in presentation.slides)

# Test image generation failure
@patch("app.tools.presentation_generator_updated.slide_generator.tools.generate_image_with_imagen3")
def test_executor_image_generation_failure(mock_generate_image, mock_slide_generator, mock_slide_data):
    mock_generate_image.return_value = None  # Simulate image generation failure
    mock_slide_generator.generate_slides.return_value = {
        "slides": [
            {
                "title": "Introduction",
                "template": "titleAndBullets",
                "content": ["Test content"],
                "image_url": "Image generation failed"
            }
        ]
    }
    with patch("app.tools.presentation_generator_updated.slide_generator.core.SlideGenerator", return_value=mock_slide_generator):
        result = executor(["Introduction"], "Test Topic", "Beginner", "en", False)
    assert result["slides"][0]["image_url"] == "Image generation failed"