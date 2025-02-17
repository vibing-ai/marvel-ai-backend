import pytest
import requests
from features.dynamo.tools import *
from app.api.error_utilities import FileHandlerError

def test_load_pdf_documents_valid():
    pdf_url = "https://filesamples.com/samples/document/pdf/sample1.pdf"
    full_content = load_pdf_documents(pdf_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_pdf_documents_invalid():
    dummy_pdf_url = "https://filesamples.com/samples/document/pdf/dummy.pdf"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_pdf_documents(dummy_pdf_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_pdf_documents_invalid_file_type():
    not_pdf_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_pdf_documents(not_pdf_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_csv_documents_valid():
    csv_url = "https://filesamples.com/samples/document/csv/sample1.csv"
    full_content = load_csv_documents(csv_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_csv_documents_invalid():
    dummy_csv_url = "https://filesamples.com/samples/document/csv/dummy.csv"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_csv_documents(dummy_csv_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404 

def test_load_csv_documents_invalid_file_type():
    not_csv_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_csv_documents(not_csv_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_txt_documents_valid():
    txt_url = "https://filesamples.com/samples/document/txt/sample1.txt"
    full_content = load_txt_documents(txt_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_txt_documents_invalid():
    dummy_txt_url = "https://filesamples.com/samples/document/txt/dummy.txt"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_txt_documents(dummy_txt_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_txt_documents_invalid_file_type():
    not_txt_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_txt_documents(not_txt_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_md_documents_valid():
    md_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md"
    full_content = load_md_documents(md_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_md_documents_invalid():
    dummy_md_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/dummy.md"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_md_documents(dummy_md_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_md_documents_invalid_file_type():
    not_md_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_md_documents(not_md_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_url_documents_valid():
    valid_url = "https://en.wikipedia.org/wiki/Gemini_(language_model)"
    full_content = load_url_documents(valid_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_pptx_documents_valid():
    pptx_url = "https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx"
    full_content = load_pptx_documents(pptx_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_pptx_documents_invalid():
    dummy_pptx_url = "https://scholar.harvard.edu/files/torman_personal/files/dummy.pptx"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_pptx_documents(dummy_pptx_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_pptx_documents_invalid_file_type():
    not_pptx_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_md_documents(not_pptx_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_docx_documents_valid():
    docx_url = "https://filesamples.com/samples/document/docx/sample1.docx"
    full_content = load_docx_documents(docx_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_docx_documents_invalid():
    dummy_docx_url = "https://filesamples.com/samples/document/docx/dummy.docx"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_docx_documents(dummy_docx_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_docx_documents_invalid_file_type():
    not_docx_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_docx_documents(not_docx_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_xls_documents_valid():
    xls_url = "https://filesamples.com/samples/document/xls/sample1.xls"
    full_content = load_xls_documents(xls_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_xls_documents_invalid():
    dummy_xls_url = "https://filesamples.com/samples/document/xls/dummy.xls"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_xls_documents(dummy_xls_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_xls_documents_invalid_file_type():
    not_xls_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_xls_documents(not_xls_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_xlsx_documents_valid():
    xlsx_url = "https://filesamples.com/samples/document/xlsx/sample1.xlsx"
    full_content = load_xlsx_documents(xlsx_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_xlsx_documents_invalid():
    dummy_xlsx_url = "https://filesamples.com/samples/document/xlsx/dummy.xlsx"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_xlsx_documents(dummy_xlsx_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_xlsx_documents_invalid_file_type():
    not_xlsx_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_xlsx_documents(not_xlsx_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_xml_documents_valid():
    xml_url = "https://filesampleshub.com/download/code/xml/sample1.xml"
    full_content = load_xml_documents(xml_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_xml_documents_invalid():
    dummy_xml_url = "https://filesampleshub.com/download/code/xml/dummy.xml"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        full_content = load_xml_documents(dummy_xml_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_xml_documents_invalid_file_type():
    not_xml_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_xml_documents(not_xml_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gdocs_documents_valid():
    gdocs_url = "https://docs.google.com/document/d/1kBzpRJYrD8KgOu0i_ATDk9TDtrDoxO-3wpm14_BGMGw/edit"
    full_content = load_gdocs_documents(gdocs_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_gdocs_documents_invalid_permission():
    private_gdocs_url = "https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1CCJBhJgkYLXM5IY/edit"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gdocs_documents(private_gdocs_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gdocs_documents_invalid_url():
    dummy_gdocs_url = "https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gdocs_documents(dummy_gdocs_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gdocs_documents_invalid_file_type():
    not_gdocs_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gdocs_documents(not_gdocs_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gsheets_documents_valid():
    gsheets_url = "https://docs.google.com/spreadsheets/d/1TTSFMXTxW_JhZ4T-K_vU3hXqWaIYwlP_X69jEiVL0KQ/edit"
    full_content = load_gsheets_documents(gsheets_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_gsheets_documents_invalid_permission():
    private_gsheets_url = "https://docs.google.com/spreadsheets/d/16OPtLLSfUptnCNpXBXqPP7GpbNTlHTBRO_bWgmH_RvU/edit"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gsheets_documents(private_gsheets_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gsheets_documents_invalid_url():
    dummy_gsheets_url = "https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gsheets_documents(dummy_gsheets_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gsheets_documents_invalid_file_type():
    not_gsheets_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gsheets_documents(not_gsheets_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gslides_documents_valid():
    gslides_url = "https://docs.google.com/presentation/d/16b6wQUyKJUOmwSgiuhUarB7tr5rgJ0TDJoSrnzIaIfA/edit"
    full_content = load_gslides_documents(gslides_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_gslides_documents_invalid_permission():
    private_gslides_url = "https://docs.google.com/presentation/d/1GeIRGJF63vyPMCeyqonluj4-8ZF0NF683LEn4J3UnhI/edit"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gslides_documents(private_gslides_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gslides_documents_invalid_url():
    dummy_gslides_url = "https://docs.google.com/presentation/d/1GeIRGJF63v683LEn4J3UnhI/edit"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gslides_documents(dummy_gslides_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gslides_documents_invalid_file_type():
    not_gslides_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gslides_documents(not_gslides_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gpdf_documents_valid():
    gpdf_url = "https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view"
    full_content = load_gpdf_documents(gpdf_url)
    assert isinstance(full_content, str)
    assert len(full_content) > 0

def test_load_gpdf_documents_invalid_permission():
    private_gpdf_url = "https://drive.google.com/file/d/1gBeAzJKTaZFwEbub8wkXr1MM-TXtw5F3/view"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gpdf_documents(private_gpdf_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gpdf_documents_invalid_url():
    dummy_gpdf_url = "https://drive.google.com/file/d/1gBeAzJKTaZFwEbub8wkXrF3/view?usp=sharing"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gpdf_documents(dummy_gpdf_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_gpdf_documents_invalid_file_type():
    not_gpdf_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md"

    with pytest.raises(FileHandlerError) as exc_info:
        full_content = load_gpdf_documents(not_gpdf_url)

    assert isinstance(exc_info.value, FileHandlerError)