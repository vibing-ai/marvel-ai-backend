import pytest
from app.features.text_rewriter.core import executor

# Base attributes reused across all tests for the text rewriter
base_attributes = {
    "original_text": "Romeo and Juliet is a tragic play by William Shakespeare that tells the story of two star-crossed lovers.",
    "instruction": "Simplify the text for a middle school audience.",
    "lang": "en",
}


# Test for plain text input (no file)
def test_executor_plain_text():
    result = executor(**base_attributes, file_url="", file_type="")
    assert isinstance(result, dict)
    assert "rewritten_text" in result


# PDF Tests
def test_executor_pdf_url_valid():
    result = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type="pdf"
    )
    assert isinstance(result, dict)
    assert "rewritten_text" in result


def test_executor_pdf_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            file_type=1  # Invalid type: should be a string
        )
    assert isinstance(exc_info.value, ValueError)


# TXT Tests
def test_executor_txt_url_valid():
    result = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt"
    )
    assert isinstance(result, dict)
    assert "rewritten_text" in result


def test_executor_txt_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            file_type=1  # Invalid type: should be a string
        )
    assert isinstance(exc_info.value, ValueError)


# Markdown Tests
def test_executor_md_url_valid():
    result = executor(
        **base_attributes,
        file_url="https://raw.githubusercontent.com/marvelai-org/marvel-ai-backend/Develop/README.md",
        file_type="md"
    )
    assert isinstance(result, dict)
    assert "rewritten_text" in result


def test_executor_md_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://raw.githubusercontent.com/marvelai-org/marvel-ai-backend/Develop/README.md",
            file_type=1  # Invalid type: should be a string
        )
    assert isinstance(exc_info.value, ValueError)
