
import pytest
from app.tools.text_rewriter.core import executor
from app.tools.text_rewriter.tools import TextRewriterValidator, RewrittenText
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
        file_url="sample.txt",
        file_type="txt",
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
