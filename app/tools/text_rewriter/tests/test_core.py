
import pytest
from app.tools.text_rewriter.core import executor
from app.tools.text_rewriter.tools import TextRewriterValidator, RewrittenText, TextRewriterPipeline, TextRewriterArgs
from app.api.error_utilities import ToolExecutorError

def test_executor_basic():
    result = executor(
        text="Hello world",
        rewrite_style="formal",
        lang="en"
    )
    assert isinstance(result, RewrittenText)
    assert result.original == "Hello world"
    assert result.style == "formal"

def test_executor_with_file():
    result = executor(
        text="Sample text",
        rewrite_style="academic",
        lang="en"
    )
    assert isinstance(result, RewrittenText)
    assert result.style == "academic"

def test_executor_empty_text():
    with pytest.raises(ValueError):
        executor(
            text="",
            rewrite_style="formal",
            lang="en"
        )

def test_executor_invalid_style():
    with pytest.raises(ValueError):
        executor(
            text="Hello world",
            rewrite_style="",
            lang="en"
        )

def test_executor_invalid_file_type():
    with pytest.raises(ToolExecutorError):
        executor(
            text="Hello world",
            rewrite_style="casual",
            file_url="test.invalid",
            file_type="invalid",
            lang="en"
        )

def test_validator():
    validator = TextRewriterValidator()
    
    assert validator.validate_text("Hello") == True
    assert validator.validate_text("") == False
    
    assert validator.validate_style("formal") == True
    assert validator.validate_style("") == False
    
    assert validator.validate_language("en") == True
    assert validator.validate_language("") == False
    assert validator.validate_language("eng") == False
    
    assert validator.validate_file_type("pdf") == True
    assert validator.validate_file_type("docx") == True
    assert validator.validate_file_type("txt") == True
    assert validator.validate_file_type("invalid") == False

def test_executor_verbose():
    result = executor(
        text="Test text",
        rewrite_style="casual",
        lang="en",
        verbose=True
    )
    assert isinstance(result, RewrittenText)
    assert hasattr(result, "changes_explained")

def test_export_docx(tmp_path):
    result = executor(
        text="Sample text for export",
        rewrite_style="formal",
        lang="en"
    )
    output_path = tmp_path / "test_output.docx"
    TextRewriterPipeline(TextRewriterArgs(
        text=result.original,
        rewrite_style=result.style
    )).export_as_docx(result, str(output_path))
    assert output_path.exists()

def test_export_pdf(tmp_path):
    result = executor(
        text="Sample text for PDF export",
        rewrite_style="academic",
        lang="en"
    )
    output_path = tmp_path / "test_output.pdf"
    TextRewriterPipeline(TextRewriterArgs(
        text=result.original,
        rewrite_style=result.style
    )).export_as_pdf(result, str(output_path))
    assert output_path.exists()

def test_url_inputs():
    # Test Website URL input
    result = executor(
        text="Sample text",
        rewrite_style="formal",
        file_url="https://example.com",
        file_type="url",
        lang="en"
    )
    assert isinstance(result, RewrittenText)

def test_url_processing():
    # Test invalid URL
    with pytest.raises(ToolExecutorError):
        executor(
            text="Sample text",
            rewrite_style="formal",
            file_url="invalid_url",
            file_type="website",
            lang="en"
        )
    
    # Test invalid file type
    with pytest.raises(ToolExecutorError):
        executor(
            text="Sample text",
            rewrite_style="formal",
            file_url="https://example.com",
            file_type="invalid",
            lang="en"
        )

def test_multiple_styles():
    styles = ["formal", "casual", "academic", "professional"]
    text = "This is a test text for multiple styles."
    
    for style in styles:
        result = executor(
            text=text,
            rewrite_style=style,
            lang="en"
        )
        assert isinstance(result, RewrittenText)
        assert result.style == style
        assert result.original == text
        assert result.rewritten != text
