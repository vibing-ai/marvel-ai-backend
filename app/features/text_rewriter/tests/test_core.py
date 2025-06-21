import pytest

from app.features.text_rewriter.core import executor

base_attributes = {
    "text_input": "Photosynthesis is a process used by plants to convert sunlight into energy.",
    "rewrite_instruction": "Summarize into bullet points",
    "lang": "en"
}


# PDF Tests
def test_executor_pdf_url_valid():
    ai_resistant_assignment = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type="pdf"
    )
    assert isinstance(ai_resistant_assignment, dict)


def test_executor_pdf_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# CSV Tests
def test_executor_csv_url_valid():
    ai_resistant_assignment = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        file_type="csv"
    )
    assert isinstance(ai_resistant_assignment, dict)


def test_executor_csv_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# TXT Tests
def test_executor_txt_url_valid():
    ai_resistant_assignment = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt"
    )
    assert isinstance(ai_resistant_assignment, dict)


def test_executor_txt_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# PPTX Tests
def test_executor_pptx_url_valid():
    ai_resistant_assignment = executor(
        **base_attributes,
        file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        file_type="pptx"
    )
    assert isinstance(ai_resistant_assignment, dict)


def test_executor_pptx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


def test_executor_xls_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/xls/sample1.xls",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


def test_executor_xlsx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# XML Tests
def test_executor_xml_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesampleshub.com/download/code/xml/dummy.xml",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# GSheets Tests
def test_executor_gsheets_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)
