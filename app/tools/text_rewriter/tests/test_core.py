import pytest
from app.tools.text_rewriter.core import executor

default_params = {
    "raw_text": "",
    "rewrite_instructions": "simplify",
    "lang": "en"
}

# PDF Tests
def test_executor_pdf_url_valid():

    rewritten_text = executor(
        **default_params,
        file_url = "https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type = "pdf"
    )
    
    assert isinstance(rewritten_text, dict)

def test_executor_pdf_url_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            **default_params,
            file_url = "https://filesamples.com/samples/document/pdf/sample1.pdf",
            file_type = 1
        )

    assert isinstance(exc_info.value, ValueError)

# CSV Tests
def test_executor_csv_url_valid():
    
    rewritten_text = executor(
        **default_params,
        file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        file_type="csv"
    )
    
    assert isinstance(rewritten_text, dict)

def test_executor_csv_url_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            **default_params,
            file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            file_type=1
        )
    
    assert isinstance(exc_info.value, ValueError)

# TXT Tests
def test_executor_txt_url_valid():
    
    rewritten_text = executor(
        **default_params,
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt"
    )
    
    assert isinstance(rewritten_text, dict)

def test_executor_txt_url_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            **default_params,
            file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            file_type=1
        )
        
    assert isinstance(exc_info.value, ValueError)

# DOCX Tests
def test_executor_docx_url_valid():
    
    rewritten_text = executor(
        **default_params,
        file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        file_type="docx"
    )
    
    assert isinstance(rewritten_text, dict)

def test_executor_docx_url_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            **default_params,
            file_url="https://filesamples.com/samples/document/docx/sample1.docx",
            file_type=1
        )
        
    assert isinstance(exc_info.value, ValueError)

# GSheets Tests
def test_executor_gsheets_url_valid():
    
    rewritten_text = executor(
        **default_params,
        file_url="https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit?gid=0#gid=0",
        file_type="gsheet"
    )
    
    assert isinstance(rewritten_text, dict)

def test_executor_gsheets_url_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            **default_params,
            file_url="https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit?gid=0#gid=0",
            file_type=1
        )
        
    assert isinstance(exc_info.value, ValueError)

# Youtube URL Tests
def test_executor_youtube_url_valid():
    
    rewritten_text = executor(
        **default_params,
        file_url="https://www.youtube.com/watch?v=HgBpFaATdoA",
        file_type="youtube_url"
    )
    
    assert isinstance(rewritten_text, dict)

def test_executor_youtube_url_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            **default_params,
            file_url="https://www.youtube.com/watch?v=HgBpFaATdoA",
            file_type=1
        )
        
    assert isinstance(exc_info.value, ValueError)

# PPTX Tests
def test_executor_pptx_url_valid():
    
    rewritten_text = executor(
        **default_params,
        file_url = "https://getsamplefiles.com/download/pptx/sample-1.pptx",
        file_type = "pptx",
    )

    assert isinstance(rewritten_text, dict)

def test_executor_pptx_url_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            **default_params,
            file_url = "https://getsamplefiles.com/download/pptx/sample-1.pptx",
            file_type = 1,
        )

    assert isinstance(exc_info.value, ValueError)

# Not Supported file type test
def test_executor_invalid_file_type():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            **default_params,
            file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            file_type="xlsx"
        )
        
    assert isinstance(exc_info.value, ValueError)

# Raw text tests
def test_executor_plain_text_valid():
    
    rewritten_text = executor(
        raw_text="The quick brown fox jumps over the lazy dog.",
        rewrite_instructions="simplify",
        file_url="",
        file_type="",
        lang="en"
    )

    assert isinstance(rewritten_text, dict)

def test_executor_plain_text_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        executor(
            raw_text="",
            rewrite_instructions="simplify",
            file_url="",
            file_type=1,
            lang="en",
        )

    assert isinstance(exc_info.value, ValueError)