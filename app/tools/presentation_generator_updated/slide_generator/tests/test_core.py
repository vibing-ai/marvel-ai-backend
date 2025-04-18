import pytest
from app.tools.presentation_generator_updated.slide_generator.core import executor,SlideGeneratorInput
from unittest.mock import patch, MagicMock, Mock
from app.tools.presentation_generator_updated.slide_generator.tools import SlideGenerator, Slide,SlidePresentation

@pytest.fixture
def mock_slide_data():
    return {
        "slides": [
            {
                "title": "Introduction to Python",
                "template": "titleAndBullets",
                "content": ["Python is a programming language"]
            },
            {
                "title": "Basic Syntax",
                "template": "titleBody",
                "content": "Python syntax is simple"
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
    """Mock SlideGenerator instead of instantiating it."""
    with patch("app.tools.presentation_generator.slide_generator.tools.GoogleGenerativeAI"), \
         patch("app.tools.presentation_generator.slide_generator.tools.GoogleGenerativeAIEmbeddings"), \
         patch("app.tools.presentation_generator.slide_generator.tools.Chroma"):
            slide_generator = SlideGenerator()
            slide_generator.validate_slides_content = MagicMock()
            slide_generator.generate_slides = MagicMock()
            return slide_generator
#Test the executor function, we mock the generate_slides method.
def test_executor(mock_slide_data,mock_slide_generator):
    slides_titles = ["Introduction to Python", "Basic Syntax"]
    topic = "Python Programming"
    instructional_level = "Beginner"
    lang = "en"
    verbose = False
    # Create a mock instance of SlideGenerator
    mock_slide_generator.generate_slides.return_value = mock_slide_data

    # Patch SlideGenerator to return the mock instance
    with patch("app.tools.presentation_generator.slide_generator.core.SlideGenerator", return_value=mock_slide_generator):
        result = executor(slides_titles, topic, instructional_level, lang, verbose)
    # Assertions
    assert result == mock_slide_data
    mock_slide_generator.generate_slides.assert_called_once() 
   # Ensure the function was called once

#Test the executor function with missing required inputs.
def test_executor_missing_inputs():
    """Test the executor function with missing required inputs."""
    with pytest.raises(ValueError, match="Missing required inputs"):
        executor(
            slides_titles=[],
            topic="",
            instructional_level="",
            lang="en"
        )

#Test the executor function with a LoaderError.
@patch("app.tools.presentation_generator.slide_generator.tools.SlideGenerator.generate_slides")
@patch("google.auth.default")
def test_executor_loader_error(mock_auth,mock_generate_slides):
    mock_auth.return_value=(MagicMock(),"fake-project-id")
    from app.api.error_utilities import LoaderError
    mock_generate_slides.side_effect = LoaderError("Error in Slide Generator Pipeline")
    with pytest.raises(Exception) as exc_info:
        executor(slides_titles=["Intro"], topic="AI", instructional_level="Intermediate", lang="en")
    assert "Error in Slide Generator Pipeline" in str(exc_info.value)

#Test the executor function with an unexpected error.
@patch("app.tools.presentation_generator.slide_generator.tools.SlideGenerator.generate_slides")
@patch("google.auth.default")
def test_executor_unexpected_error(mock_auth,mock_generate_slides):
    mock_auth.return_value=(MagicMock(),"fake-project-id")
    mock_generate_slides.side_effect = Exception("Unexpected error occurred")
    with pytest.raises(ValueError, match="Error in executor: Unexpected error occurred"):
        executor(slides_titles=["Intro"], topic="AI", instructional_level="Intermediate", lang="en")

#Test the validate_slides_content function.
def test_validate_slides_content(mock_slide_generator):
    # Define fake return value
    mock_slide_generator.validate_slides_content.return_value = {
        "topic_coverage": 80,
        "template_requirements_met": True,
        "garbage_coverage_percentage": 0,
        "valid": True
    }
    topic = "AI in Education"
    response = {"slides": [{"template": "twoColumn", "content": ["AI and learning"]}]}
    result = mock_slide_generator.validate_slides_content(response, topic)

    assert result["valid"] == True
    assert result["topic_coverage"] == 80
    
    

#Test the validate_slides_content function with garbage content.
def test_validate_slides_content_with_garbage(mock_slide_generator):
    topic = "Introduction"
    response = {
        "slides": [
            {
                "title": "Introduction",
                "template": "sectionHeader",  # Not "twoColumn"
                "content": ["Unrelated content", "* This should not be here"]
            }
        ]
    }
    # Mock the return value for an invalid response
    mock_slide_generator.validate_slides_content.return_value = {
        "topic_coverage": 20,
        "template_requirements_met": False,
        "garbage_coverage_percentage": 50,
        "valid": False
    }
    result = mock_slide_generator.validate_slides_content(response, topic)

    assert result["valid"] == False
    assert result["topic_coverage"] == 20
    assert result["template_requirements_met"] == False
    assert result["garbage_coverage_percentage"] == 50


#Test the validate_slides_content function with empty slides.
def test_validate_slides_content_empty_slides(mock_slide_generator):
    topic = "Introduction"
    response = {"slides": []}  # No slides

    # Mock the method to raise ValueError when slides are empty
    mock_slide_generator.validate_slides_content.side_effect = ValueError("No slides found in the response")

    with pytest.raises(ValueError, match="No slides found in the response"):
        mock_slide_generator.validate_slides_content(response, topic)

#Test the compile_with_context function.
def test_slide_generator_compile_context(mock_args,mock_slide_generator):
    """Test compilation of pipeline."""
    args = mock_args
    test_instance = mock_slide_generator
    test_instance.args = args    
    chain = test_instance.compile_context()    
    assert chain is not None


#Test the Slide Pydantic model.
def test_slide_model():
    """Test the Slide Pydantic model."""
    slide = Slide(
        title="Introduction",
        template="titleAndBullets",
        content=["Key Point 1", "Key Point 2"]
    )
    
    assert slide.title == "Introduction"
    assert slide.template == "titleAndBullets"
    assert slide.content == ["Key Point 1", "Key Point 2"]
    
#Test the SlidePresentation Pydantic model.
def test_slide_presentation_model():
    """Test the SlidePresentation Pydantic model."""
    slides = [
        Slide(title="Intro", template="titleAndBody", content="Overview"),
        Slide(title="Details", template="twoColumn", content={"left": "Content1", "right": "Content2"})
    ]
    
    presentation = SlidePresentation(slides=slides)
    
    assert len(presentation.slides) == 2
    assert all(isinstance(slide, Slide) for slide in presentation.slides)
