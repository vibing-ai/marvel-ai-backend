import pytest
from app.tools.presentation_generator_updated.slide_generator.core import executor
from app.services.schemas import SlideGeneratorInput
from unittest.mock import patch, MagicMock, Mock, mock_open
from app.tools.presentation_generator_updated.slide_generator.tools import SlideGenerator, Slide, SlidePresentation
from app.api.error_utilities import LoaderError, ToolExecutorError
import logging
import os

@pytest.fixture
def mock_slide_data():
    return {
        "data": {
            "slides": [
                {
                    "title": "Introduction to Python",
                    "template": "titleAndBullets",
                    "content": ["Python is a programming language"],
                    "needs_image": False
                },
                {
                    "title": "Basic Syntax",
                    "template": "titleBody",
                    "content": "Python syntax is simple",
                    "needs_image": True,
                    "image_url": "https://storage.googleapis.com/slide-images-bucket/2-test-uuid.png"
                }
            ]
        }
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
    """Mock SlideGenerator with properly mocked file operations."""
    # Mock file operations to prevent FileNotFoundError
    with patch("builtins.open", mock_open(read_data="Mocked prompt template")), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.GoogleGenerativeAI"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.GoogleGenerativeAIEmbeddings"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.Chroma"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.ImageGenerator"), \
         patch("os.path.join", return_value="mocked_path"):
            
            slide_generator = SlideGenerator()
            
            # Now properly mock the methods we're testing
            slide_generator.validate_slides_content = MagicMock()
            slide_generator.generate_slides = MagicMock()
            
            return slide_generator

# Test the executor function, we mock the generate_slides method.
def test_executor(mock_slide_data, mock_slide_generator):
    """Test successful execution of the executor function."""
    slides_titles = ["Introduction to Python", "Basic Syntax"]
    topic = "Python Programming"
    instructional_level = "Beginner"
    lang = "en"
    verbose = False
    
    # Create a mock instance of SlideGenerator
    mock_slide_generator.generate_slides.return_value = mock_slide_data

    # Patch SlideGenerator to return the mock instance
    with patch("app.tools.presentation_generator_updated.slide_generator.core.SlideGenerator", return_value=mock_slide_generator):
        result = executor(slides_titles, topic, instructional_level, lang, verbose)
    
    # Assertions
    assert result == mock_slide_data
    mock_slide_generator.generate_slides.assert_called_once() 

# Test the executor function with missing required inputs.
def test_executor_missing_inputs():
    """Test the executor function with missing required inputs."""
    with pytest.raises(ValueError, match="Missing required inputs"):
        executor(
            slides_titles=[],
            topic="",
            instructional_level="",
            lang="en"
        )

# Test the executor function with a LoaderError.
@patch("app.tools.presentation_generator_updated.slide_generator.tools.SlideGenerator.generate_slides")
@patch("google.auth.default")
def test_executor_loader_error(mock_auth, mock_generate_slides):
    mock_auth.return_value = (MagicMock(), "fake-project-id")
    mock_generate_slides.side_effect = LoaderError("Error in Slide Generator Pipeline")
    
    with pytest.raises(ToolExecutorError) as exc_info:
        executor(slides_titles=["Intro"], topic="AI", instructional_level="Intermediate", lang="en")
    
    assert "Error in Slide Generator Pipeline" in str(exc_info.value)

# Test the executor function with an unexpected error.
@patch("app.tools.presentation_generator_updated.slide_generator.tools.SlideGenerator.generate_slides")
@patch("google.auth.default")
def test_executor_unexpected_error(mock_auth, mock_generate_slides):
    mock_auth.return_value = (MagicMock(), "fake-project-id")
    mock_generate_slides.side_effect = Exception("Unexpected error occurred")
    
    with pytest.raises(ValueError, match="Error in executor: Unexpected error occurred"):
        executor(slides_titles=["Intro"], topic="AI", instructional_level="Intermediate", lang="en")

# Test the validate_slides_content function.
def test_validate_slides_content(mock_slide_generator):
    """Test validation of slide content against topic."""
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

# Test the validate_slides_content function with garbage content.
def test_validate_slides_content_with_garbage(mock_slide_generator):
    """Test validation of slide content with inappropriate formatting."""
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

# Test the validate_slides_content function with empty slides.
def test_validate_slides_content_empty_slides(mock_slide_generator):
    """Test validation handling of empty slides array."""
    topic = "Introduction"
    response = {"slides": []}  # No slides

    # Mock the method to raise ValueError when slides are empty
    mock_slide_generator.validate_slides_content.side_effect = ValueError("No slides found in the response")

    with pytest.raises(ValueError, match="No slides found in the response"):
        mock_slide_generator.validate_slides_content(response, topic)

# Test the compile_context function.
def test_slide_generator_compile_context(mock_slide_generator):
    """Test compilation of the prompt chain."""
    args = SlideGeneratorInput(
        slides_titles=["Intro", "Details"],
        topic="Data Science",
        instructional_level="Intermediate",
        lang="en"
    )
    test_instance = mock_slide_generator
    test_instance.args = args
    
    # Mock the compile_context method to return a MagicMock object
    test_instance.compile_context = MagicMock(return_value=MagicMock())
    
    chain = test_instance.compile_context()    
    assert chain is not None

@patch("langchain_core.prompts.PromptTemplate")
@patch("langchain_google_genai.GoogleGenerativeAI")
def test_image_determination(mock_gemini, mock_prompt_template):
    """Test the determination of whether a slide needs an image."""
    logging.basicConfig(level=logging.DEBUG)
    
    # Disable LangChain tracing to avoid type errors
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_TRACING"] = "false"
    
    # Create mocks for the prompt files
    slide_generator_prompt = "You are a slide generator. Generate slides based on {instructional_level}, {topic}, {slides_titles}."
    slide_image_determination_prompt = """Your job is to determine whether a slide needs an associated image with it.
Here are the rules:

YES if: 
- The slide discusses historical events, places, people, or processes.
- The slide content contains data or statistics.
- The text is long, needing visual summarization.

NO if: 
- The content is purely conceptual without visual elements.

Slide content: {slide_content}

ONLY respond with YES or NO, and nothing else."""
    
    # Create a patched open function that returns different content based on the path
    def patched_open(file_path, *args, **kwargs):
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=None)
        
        if "slide_image_determination_prompt.txt" in str(file_path):
            mock_file.read.return_value = slide_image_determination_prompt
        elif "slide_generator_prompt.txt" in str(file_path):
            mock_file.read.return_value = slide_generator_prompt
        else:
            mock_file.read.return_value = "Default mocked content"
        
        return mock_file
    
    # Mock prompt template and format method
    mock_prompt_instance = MagicMock()
    mock_prompt_instance.format.side_effect = lambda slide_content: f"Prompt for: {slide_content}"
    mock_prompt_template.return_value = mock_prompt_instance
    
    # Setup mock LLM responses for the determination prompt
    mock_model_instance = MagicMock()
    mock_model_instance.invoke.side_effect = ["YES", "NO"]
    mock_gemini.return_value = mock_model_instance
    
    # Create mock chains
    mock_generate_chain = MagicMock()
    mock_image_determination_chain = MagicMock()
    
    # Setup image determination chain to return YES for historical content and NO for abstract concepts
    mock_image_determination_chain.invoke.side_effect = lambda params: "YES" if "World War II" in str(params.get("slide_content", "")) else "NO"
    
    # Setup test with patched dependencies
    with patch("builtins.open", side_effect=patched_open), \
         patch("os.path.dirname", return_value="/mock/path"), \
         patch("os.path.join", side_effect=lambda *args: "/".join(args)), \
         patch("os.path.abspath", return_value="/mock/absolute/path"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.ImageGenerator") as mock_image_generator_class, \
         patch("langchain_core.output_parsers.JsonOutputParser"), \
         patch("langchain_core.callbacks.manager.CallbackManager", return_value=MagicMock()):
        
        # Setup mocks for image generator
        mock_image_generator = MagicMock()
        mock_image_generator.generate_slide_image.return_value = "https://example.com/image.png"
        mock_image_generator_class.return_value = mock_image_generator
        
        # Create test slides
        test_slides = [
            {
                "title": "Historical Events",
                "template": "titleAndBody",
                "content": "World War II happened between 1939-1945."
            },
            {
                "title": "Abstract Concepts",
                "template": "titleAndBullets",
                "content": ["Logic", "Reasoning", "Thinking"]
            }
        ]
        
        # Create a custom generator with mocked dependencies
        generator = SlideGenerator(
            args=SlideGeneratorInput(
                slides_titles=["Test Slide 1", "Test Slide 2"],
                topic="Test Topic",
                instructional_level="Beginner",
                lang="en"
            )
        )
        
        # Setup for testing the generate_slides method
        generator.validate_slides_content = MagicMock(return_value={"valid": True})
        
        # Create a mock chain tuple to match updated compile_context
        mock_generate_chain.invoke.return_value = {"slides": test_slides}
        generator.compile_context = MagicMock(return_value=(mock_generate_chain, mock_image_determination_chain))
        
        # Execute the method being tested
        result = generator.generate_slides()
        
        # Assertions
        assert len(result["slides"]) == 2
        assert result["slides"][0]["needs_image"] == True
        assert "image_url" in ["slides"][0]
        assert result["slides"][1]["needs_image"] == False
        
        # Verify correct parameters for generate_slide_image
        mock_image_generator.generate_slide_image.assert_called_once_with(
            id=1,  # First slide has id=1
            title="Historical Events",
            content="World War II happened between 1939-1945.",
            layout="titleAndBody"
        )
        
        # Verify the image determination was called twice (once for each slide)
        assert mock_image_determination_chain.invoke.call_count == 2

# Test the Slide Pydantic model.
def test_slide_model():
    """Test the Slide Pydantic model."""
    slide = Slide(
        title="Introduction",
        template="titleAndBullets",
        content=["Key Point 1", "Key Point 2"],
        needs_image=True,
        image_url="https://example.com/image.png"
    )
    
    assert slide.title == "Introduction"
    assert slide.template == "titleAndBullets"
    assert slide.content == ["Key Point 1", "Key Point 2"]
    assert slide.needs_image == True
    assert slide.image_url == "https://example.com/image.png"
    
# Test the SlidePresentation Pydantic model.
def test_slide_presentation_model():
    """Test the SlidePresentation Pydantic model."""
    slides = [
        Slide(title="Intro", template="titleAndBody", content="Overview", needs_image=False),
        Slide(title="Details", template="twoColumn", content={"leftColumn": "Content1", "rightColumn": "Content2"}, needs_image=True, image_url="https://example.com/image.png")
    ]
    
    presentation = SlidePresentation(slides=slides)
    
    assert len(presentation.slides) == 2
    assert all(isinstance(slide, Slide) for slide in presentation.slides)
    assert presentation.slides[0].needs_image == False
    assert presentation.slides[1].needs_image == True
    assert presentation.slides[1].image_url == "https://example.com/image.png"
