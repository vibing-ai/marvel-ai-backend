import pytest
from app.tools.presentation_generator.core import executor

# Base attributes reused across all tests
base_attributes = {
    "grade_level": "5th grade",
    "n_slides": 10,
    "topic": "Mathematics",
    "objectives": "",
    "additional_comments": "",
    "additional_comments_file_url": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true",
    "additional_comments_file_type": "gdoc",
    "lang": "en"
}

# PDF Tests
def test_executor_pdf_objectives_url_valid():
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        objectives_file_type="pdf"
    )
    assert isinstance(presentation, dict)

def test_executor_pdf_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# CSV Tests
def test_executor_csv_objectives_url_valid():
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        objectives_file_type="csv"
    )
    assert isinstance(presentation, dict)

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
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        objectives_file_type="txt"
    )
    assert isinstance(presentation, dict)

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
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        objectives_file_type="md"
    )
    assert isinstance(presentation, dict)

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
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        objectives_file_type="pptx"
    )
    assert isinstance(presentation, dict)

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
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        objectives_file_type="docx"
    )
    assert isinstance(presentation, dict)

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
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
        objectives_file_type="xls"
    )
    assert isinstance(presentation, dict)

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
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        objectives_file_type="xlsx"
    )
    assert isinstance(presentation, dict)

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
    presentation = executor(
        **base_attributes,
        objectives_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        objectives_file_type="gpdf"
    )
    assert isinstance(presentation, dict)

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