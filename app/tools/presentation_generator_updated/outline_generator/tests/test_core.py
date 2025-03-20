import pytest
from unittest.mock import MagicMock, patch
from app.tools.presentation_generator_updated.outline_generator.core import executor
from app.tools.presentation_generator_updated.outline_generator.tools import OutlineGenerator, Outlines
from app.services.schemas import OutlineGeneratorInput
from app.api.error_utilities import LoaderError, ToolExecutorError
from langchain_core.documents import Document
from unittest.mock import Mock
# Base test attributes
base_attributes = {
    "n_slides": 2,
    "topic": "Introduction to Python Programming",
    "instructional_level": "beginner",
    "file_url": "",
    "file_type": "",
    "lang": "en"
}

# Mock OutlineGeneratorInput
mock_args = OutlineGeneratorInput(
    n_slides=base_attributes["n_slides"],
    topic=base_attributes["topic"],
    instructional_level=base_attributes["instructional_level"],
    file_url=base_attributes["file_url"],
    file_type=base_attributes["file_type"],
    lang=base_attributes["lang"]
)
@pytest.fixture
def mock_outline_data():
    return {
        "outlines": [
            "Introduction to Python Programming",
            "Basic Syntax"
        ]
    }
@pytest.fixture
def mock_outline_generator():
    with patch("app.tools.presentation_generator.slide_generator.tools.GoogleGenerativeAI", autospec=True) as mock_model, \
         patch("app.tools.presentation_generator.slide_generator.tools.GoogleGenerativeAIEmbeddings", autospec=True) as mock_embeddings, \
         patch("app.tools.presentation_generator.slide_generator.tools.JsonOutputParser", autospec=True) as mock_parser, \
         patch("app.tools.presentation_generator.slide_generator.tools.Chroma", autospec=True) as mock_chroma:
        # Create mock objects for the dependencies
        mock_model_instance = mock_model.return_value
        mock_embeddings_instance = mock_embeddings.return_value
        mock_parser_instance = mock_parser.return_value
        mock_chroma_instance = mock_chroma.return_value

        # Create a mock SlideGenerator instance
        outline_generator = OutlineGenerator()

        # Override attributes with mocks
        outline_generator.model = mock_model_instance
        outline_generator.embedding_model = mock_embeddings_instance
        outline_generator.parser = mock_parser_instance
        outline_generator.vectorstore_class = mock_chroma_instance
        yield outline_generator

# Test OutlineGenerator class initialization
def test_outline_generator_init():
    """Test initialization of OutlineGenerator."""
    generator = OutlineGenerator(args=mock_args, verbose=False)
    assert generator.args is not None
    assert generator.verbose is False
    assert generator.vectorstore is None
    assert generator.retriever is None
    assert generator.runner is None

# Test the executor function (integration test)
def test_executor_normal_operation(mock_outline_data):
    """Test the executor function with valid inputs."""

    # Set up mock returns
    mock_outline_generator = MagicMock()
    mock_outline_generator.generate_outline.return_value = mock_outline_data
    # Patch OutlineGenerator to return the mock instance
    with patch("app.tools.presentation_generator.outline_generator.core.OutlineGenerator", return_value=mock_outline_generator):
        result = executor(
            n_slides=base_attributes["n_slides"],
            topic=base_attributes["topic"],
            instructional_level=base_attributes["instructional_level"],
            file_url=base_attributes["file_url"],
            file_type=base_attributes["file_type"],
            lang=base_attributes["lang"],
            verbose=False
        )
  
    # Check if the result is a dictionary instead of an Outlines instance
    assert result == mock_outline_data
    # Ensure the function was called once
    mock_outline_generator.generate_outline.assert_called_once()

    # Validate the structure of the dictionary
    assert "outlines" in result, "Key 'outlines' not found in response"
    assert isinstance(result["outlines"], list), "Expected 'outlines' to be a list"
    

def test_executor_missing_required_inputs():
    """Test the executor function with missing required inputs."""
    with pytest.raises(ValueError):
        result =  executor(
                n_slides=None,
                topic=None,
                instructional_level=base_attributes["instructional_level"],
                file_url=base_attributes["file_url"],
                file_type=base_attributes["file_type"],
                lang=base_attributes["lang"],
                verbose=False
            )
# Test OutlineGenerator with invalid arguments
def test_outline_generator_init_missing_params():
    """Test initialization of OutlineGenerator with missing parameters."""

    with pytest.raises(ValueError, match="Topic must be provided"):
        OutlineGenerator(args=Mock(topic=None, lang="en"))
    
    with pytest.raises(ValueError, match="Language must be provided"):
        OutlineGenerator(args=Mock(topic="Test", lang=None))


def test_outline_generator_compile_without_context(mock_outline_generator):
    """Test compilation of pipeline without context."""
    args = OutlineGeneratorInput(
        n_slides=3,
        topic="Machine Learning",
        instructional_level="Advanced",
        file_url="",
        file_type="",
        lang="en"
    )
    
    generator = OutlineGenerator(args=args)
    chain = generator.compile_without_context()
    
    assert chain is not None

def test_outlines_model():
    """Test the Outlines Pydantic model."""
    outlines = Outlines(
        outlines=[
            "Introduction to Cybersecurity",
            "Types of Cyber Threats",
            "Basic Security Practices"
        ]
    )    
    assert len(outlines.outlines) == 3
    assert all(isinstance(outline, str) for outline in outlines.outlines)