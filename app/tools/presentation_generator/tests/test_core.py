import pytest
from app.tools.presentation_generator.core import executor
from app.api.error_utilities import ToolExecutorError  # Added this import

# Base attributes reused across all tests, aligned with PRD's core inputs
base_attributes = {
    "instructionalLevel": "High School",
    "slideCount": 5,
    "text": "World War II Overview"
}

# Core Functionality Tests
def test_executor_basic_valid():
    presentation = executor(**base_attributes)
    assert isinstance(presentation, dict)
    assert "main_title" in presentation
    assert "list_slides" in presentation
    assert len(presentation["list_slides"]) == base_attributes["slideCount"]
    assert all("template" in slide for slide in presentation["list_slides"])

def test_executor_invalid_slide_count_below_range():
    with pytest.raises(ValueError) as exc_info:
        executor(instructionalLevel="High School", slideCount=4, text="World War II")
    assert "Number of slides must be between 5 and 20" in str(exc_info.value)

def test_executor_invalid_slide_count_above_range():
    with pytest.raises(ValueError) as exc_info:
        executor(instructionalLevel="High School", slideCount=21, text="World War II")
    assert "Number of slides must be between 5 and 20" in str(exc_info.value)

def test_executor_missing_text():
    with pytest.raises(ValueError) as exc_info:
        executor(instructionalLevel="High School", slideCount=5, text="")
    assert "Topic must be provided" in str(exc_info.value)

def test_executor_missing_instructional_level():
    with pytest.raises(ValueError) as exc_info:
        executor(instructionalLevel="", slideCount=5, text="World War II")
    assert "Instructional level must be provided" in str(exc_info.value)

# Optional File-Based Tests (Reduced Set)
def test_executor_pdf_objectives_url_valid():
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        objectives_file_type="pdf"
    )
    assert isinstance(presentation, dict)
    assert "main_title" in presentation
    assert len(presentation["list_slides"]) == base_attributes["slideCount"]

def test_executor_pdf_objectives_url_invalid_type():
    with pytest.raises(ToolExecutorError):  # Now defined with the import
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            objectives_file_type=1  # Invalid type
        )

def test_executor_gdoc_additional_comments_url_valid():
    presentation = executor(
        **base_attributes,
        additional_comments_file_url="https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing",
        additional_comments_file_type="gdoc"
    )
    assert isinstance(presentation, dict)
    assert "main_title" in presentation
    assert len(presentation["list_slides"]) == base_attributes["slideCount"]