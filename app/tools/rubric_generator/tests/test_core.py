import pytest
from unittest.mock import patch, MagicMock
from app.tools.rubric_generator.core import executor, validate_file_type
from app.api.error_utilities import ToolExecutorError

# Base attributes reused across all tests
base_attributes = {
    "grade_level": "9th Grade",
    "point_scale": 4,
    "objectives": "Write an argumentative essay with clear thesis and supporting evidence.",
    "assignment_description": "Write a 3-5 page argumentative essay on a topic of your choice.",
    "additional_customization": "Include a section for peer review feedback.",
    "lang": "en"
}

# Test file types and their corresponding test URLs
test_file_types = [
    ("pdf", "https://example.com/sample.pdf"),
    ("docx", "https://example.com/sample.docx"),
    ("pptx", "https://example.com/sample.pptx"),
    ("txt", "https://example.com/sample.txt"),
    ("youtube", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    ("website", "https://example.com"),
    ("gsheet", "https://docs.google.com/spreadsheets/d/1Xy3N1wHcZQ6oY1qXyZ2Z3X4v5b6n7m8o9p0q1r2s3t4u5v6w7x8y9z0")
]

# Test basic rubric generation
def test_executor_basic():
    """Test basic rubric generation with minimal required fields."""
    rubric = executor(
        grade_level="9th Grade",
        point_scale=4,
        objectives="Test objectives",
        assignment_description="Test description"
    )
    assert isinstance(rubric, dict)
    assert "title" in rubric
    assert "criterias" in rubric
    assert len(rubric["criterias"]) > 0

# Test file type validation
def test_validate_file_type_valid():
    """Test validation of supported file types."""
    for file_type, _ in test_file_types:
        validate_file_type(file_type, "test_field")

def test_validate_file_type_invalid():
    """Test validation of unsupported file types."""
    with pytest.raises(ValueError):
        validate_file_type("invalid_type", "test_field")

# Test with only file inputs
@patch('app.tools.rubric_generator.core.get_docs')
def test_executor_file_inputs_only(mock_get_docs):
    """Test rubric generation with only file inputs (no direct text inputs)."""
    mock_get_docs.return_value = []
    
    rubric = executor(
        grade_level="9th Grade",
        point_scale=4,
        objectives="",
        assignment_description="",
        objectives_file_url="https://example.com/objectives.pdf",
        objectives_file_type="pdf",
        assignment_description_file_url="https://example.com/assignment.pdf",
        assignment_description_file_type="pdf",
        lang="en"
    )
    
    assert isinstance(rubric, dict)
    assert "title" in rubric
    assert "criterias" in rubric
    mock_get_docs.assert_called()

# Test with additional customization
def test_executor_with_customization():
    """Test that additional customization is properly incorporated into the rubric."""
    rubric = executor(
        grade_level="9th Grade",
        point_scale=4,
        objectives="Test objectives",
        assignment_description="Test description",
        additional_customization="Include specific criteria for creativity and originality"
    )
    
    assert isinstance(rubric, dict)
    assert any(
        any("creativity" in level["description"].lower() or 
            "originality" in level["description"].lower()
            for level in criteria["criteria_description"])
        for criteria in rubric.get("criterias", [])
    )

# Test input validation
def test_executor_missing_required():
    """Test that required fields are properly validated."""
    # Missing grade_level
    with pytest.raises(ValueError, match="Grade level is required"):
        executor(
            grade_level="",
            point_scale=4,
            objectives="test",
            assignment_description="test"
        )
    
    # Invalid point scale
    with pytest.raises(ValueError, match="Point scale must be an integer between 2 and 10"):
        executor(
            grade_level="9th Grade",
            point_scale=1,  # Too low
            objectives="test",
            assignment_description="test"
        )
    
    with pytest.raises(ValueError, match="Point scale must be an integer between 2 and 10"):
        executor(
            grade_level="9th Grade",
            point_scale=11,  # Too high
            objectives="test",
            assignment_description="test"
        )

# Test file type handling
@pytest.mark.parametrize("file_type,url", test_file_types)
@patch('app.tools.rubric_generator.core.get_docs')
def test_file_type_handling(mock_get_docs, file_type, url):
    """Test that different file types are handled correctly."""
    mock_get_docs.return_value = []
    
    rubric = executor(
        grade_level="9th Grade",
        point_scale=4,
        objectives="Test objectives" if file_type not in ["youtube", "website", "gsheet"] else "",
        assignment_description="Test description",
        objectives_file_url=url if file_type in ["youtube", "website", "gsheet"] else "",
        objectives_file_type=file_type if file_type in ["youtube", "website", "gsheet"] else "",
        lang="en"
    )
    
    assert isinstance(rubric, dict)
    assert "title" in rubric
    
    # For regular files, verify get_docs was called
    if file_type not in ["youtube", "website", "gsheet"]:
        mock_get_docs.assert_not_called()
    else:
        # For special URL types, we don't call get_docs directly
        mock_get_docs.assert_not_called()

# Test error handling for invalid file types
def test_invalid_file_type():
    """Test that invalid file types raise appropriate errors."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        executor(
            grade_level="9th Grade",
            point_scale=4,
            objectives="",
            assignment_description="",
            objectives_file_url="https://example.com/test.invalid",
            objectives_file_type="invalid_type"
        )

# Test with all fields provided
def test_complete_workflow():
    """Test the complete workflow with all possible fields provided."""
    rubric = executor(
        grade_level="9th Grade",
        point_scale=4,
        objectives="Write a research paper with proper citations.",
        assignment_description="5-page research paper on a historical event.",
        additional_customization="Focus on thesis clarity and source reliability.",
        lang="en"
    )
    
    assert isinstance(rubric, dict)
    assert "title" in rubric
    assert "criterias" in rubric
    assert len(rubric["criterias"]) >= 3  # Should have at least 3 criteria
    
    # Verify some common criteria would be included
    criteria_titles = [c["criteria"].lower() for c in rubric["criterias"]]
    assert any("thesis" in title or "argument" in title for title in criteria_titles)
    assert any("research" in title or "sources" in title for title in criteria_titles)
    assert any("organization" in title or "structure" in title for title in criteria_titles)

# CSV Tests
def test_executor_csv_objectives_url_valid():
    rubric = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        objectives_file_type="csv"
    )
    assert isinstance(rubric, dict)

def test_executor_csv_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# TXT Tests
def test_executor_txt_objectives_url_valid():
    rubric = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        objectives_file_type="txt"
    )
    assert isinstance(rubric, dict)

def test_executor_txt_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# MD Tests
def test_executor_md_objectives_url_valid():
    rubric = executor(
        **base_attributes,
        objectives_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        objectives_file_type="md"
    )
    assert isinstance(rubric, dict)

def test_executor_md_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# PPTX Tests
def test_executor_pptx_objectives_url_valid():
    rubric = executor(
        **base_attributes,
        objectives_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        objectives_file_type="pptx"
    )
    assert isinstance(rubric, dict)

def test_executor_pptx_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# DOCX Tests
def test_executor_docx_objectives_url_valid():
    rubric = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        objectives_file_type="docx"
    )
    assert isinstance(rubric, dict)

def test_executor_docx_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLS Tests
def test_executor_xls_objectives_url_valid():
    rubric = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
        objectives_file_type="xls"
    )
    assert isinstance(rubric, dict)

def test_executor_xls_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLSX Tests
def test_executor_xlsx_objectives_url_valid():
    rubric = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        objectives_file_type="xlsx"
    )
    assert isinstance(rubric, dict)

def test_executor_xlsx_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# GPDF Tests
def test_executor_gpdf_objectives_url_valid():
    rubric = executor(
        **base_attributes,
        objectives_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        objectives_file_type="gpdf"
    )
    assert isinstance(rubric, dict)

def test_executor_gpdf_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# MP3 Tests
def test_executor_mp3_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)