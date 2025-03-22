import pytest
from app.api.error_utilities import SyllabusGeneratorError
from app.tools.syllabus_generator.core import executor

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Base attributes reused across all tests
base_attributes = {
    "grade_level": "5th grade",
    "subject": "Math",
    "course_description": "This course covers basic arithmetic operations.",
    "objectives": "Understand addition, subtraction, multiplication, and division.",
    "required_materials": "Notebook, pencils, calculator.",
    "grading_policy": "Homework 40%, Exams 60%.",
    "policies_expectations": "Complete assignments on time, participate in class.",
    "course_outline": "Week 1: Addition; Week 2: Subtraction; Week 3: Multiplication.",
    "additional_notes": "Bring a calculator every day.",
    "lang": "en"
}

# PDF Tests
def test_executor_pdf_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type="pdf"
    )
    assert isinstance(syllabus, dict)

def test_executor_pdf_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# CSV Tests
def test_executor_csv_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        file_type="csv"
    )
    assert isinstance(syllabus, dict)

def test_executor_csv_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# TXT Tests
def test_executor_txt_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt"
    )
    assert isinstance(syllabus, dict)

def test_executor_txt_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# MD Tests
def test_executor_md_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        file_type="md"
    )
    assert isinstance(syllabus, dict)

def test_executor_md_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# PPTX Tests
def test_executor_pptx_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        file_type="pptx"
    )
    assert isinstance(syllabus, dict)

def test_executor_pptx_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# DOCX Tests
def test_executor_docx_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        file_type="docx"
    )
    assert isinstance(syllabus, dict)

def test_executor_docx_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/docx/sample1.docx",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# XLS Tests
def test_executor_xls_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/xls/sample1.xls",
        file_type="xls"
    )
    assert isinstance(syllabus, dict)

def test_executor_xls_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/xls/sample1.xls",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# XLSX Tests
def test_executor_xlsx_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        file_type="xlsx"
    )
    assert isinstance(syllabus, dict)

def test_executor_xlsx_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# XML Tests
def test_executor_xml_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesampleshub.com/download/code/xml/dummy.xml",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# GDocs Tests
def test_executor_gdocs_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# GSheets Tests
def test_executor_gsheets_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# GSlides Tests
def test_executor_gslides_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# GPDFs Tests
def test_executor_gpdfs_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        file_type="gpdf"
    )
    assert isinstance(syllabus, dict)

def test_executor_gpdfs_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# MP3 Tests
def test_executor_mp3_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            file_type=1
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)