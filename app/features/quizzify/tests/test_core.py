import pytest
from app.features.quizzify.core import executor
# from app.api.error_utilities import SyllabusGeneratorError
from app.services.schemas import QuizzifyArgs

def test_executor_pdf_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type = "pdf"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_pdf_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/pdf/dummy.pdf",
        file_type = "pdf"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_csv_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/csv/sample1.csv",
        file_type = "csv"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_csv_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/csv/dummy.csv",
        file_type = "csv"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_txt_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/txt/sample1.txt",
        file_type = "txt"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_txt_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/txt/dummy.txt",
        file_type = "txt"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_md_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        file_type = "md"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_md_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/dummy.md",
        file_type = "md"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_pptx_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        file_type = "pptx"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_pptx_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/samplepptx.pptx",
        file_type = "pptx"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_docx_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/docx/sample1.docx",
        file_type = "docx"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_docx_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/docx/dummy.docx",
        file_type = "docx"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_xls_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/xls/sample1.xls",
        file_type = "xls"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_xls_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/xls/dummy.xls",
        file_type = "xls"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_xlsx_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        file_type = "xlsx"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_xlsx_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesamples.com/samples/document/xlsx/dummy.xlsx",
        file_type = "xlsx"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_xml_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesampleshub.com/download/code/xml/sample1.xml",
        file_type = "xml"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_xml_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://filesampleshub.com/download/code/xml/dummy.xml",
        file_type = "xml"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_gdocs_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://docs.google.com/document/d/1kBzpRJYrD8KgOu0i_ATDk9TDtrDoxO-3wpm14_BGMGw/edit",
        file_type = "gdoc"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_gdocs_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit",
        file_type = "gdoc"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_gsheets_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://docs.google.com/spreadsheets/d/1TTSFMXTxW_JhZ4T-K_vU3hXqWaIYwlP_X69jEiVL0KQ/edit",
        file_type = "gsheet"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_gsheets_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
        file_type = "gsheet"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_gslides_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://docs.google.com/presentation/d/16b6wQUyKJUOmwSgiuhUarB7tr5rgJ0TDJoSrnzIaIfA/edit",
        file_type = "gslide"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_gslides_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
        file_type = "gslide"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_gpdfs_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "doc",
        n_questions = 1,
        file_url = "https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        file_type = "gpdf"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_gpdfs_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://drive.google.com/file/d/1gBeAzJKTaZFwEbub8wkXrF3/view?usp=sharing",
        file_type = "gpdf"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_mp3_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://github.com/asleem/uploaded_files/raw/refs/heads/main/Burnett.mp3",
        file_type = "mp3"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_mp3_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
        file_type = "mp3"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)

def test_executor_gmp3_url_valid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://github.com/asleem/uploaded_files/raw/refs/heads/main/Burnett.mp3",
        file_type = "gmp3"
    )

    quiz = executor(quizzify_args)

    assert isinstance(quiz, list)
    assert len(quiz) == quizzify_args.n_questions

def test_executor_gmp3_url_invalid():
    quizzify_args = QuizzifyArgs(
        topic = "college",
        n_questions = 1,
        file_url = "https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
        file_type = "gmp3"
    )

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(quizzify_args)

    assert isinstance(exc_info.value, ValueError)