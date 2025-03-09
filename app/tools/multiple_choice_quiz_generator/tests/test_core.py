import pytest
from app.tools.multiple_choice_quiz_generator.core import executor

def test_executor_pdf_url_valid():

    n_questions = 1

    quiz = executor(
        topic = "college",
        n_questions = n_questions,
        file_url = "https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type = "pdf",
        lang = "en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_pdf_url_invalid():
    
    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://filesamples.com/samples/document/pdf/sample1.pdf",
            file_type = "pdf",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_csv_url_valid():
    n_questions = 1

    quiz = executor(
        topic = "college",
        n_questions = n_questions,
        file_url = "https://filesamples.com/samples/document/csv/sample1.csv",
        file_type = "csv",
        lang = "en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_csv_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://filesamples.com/samples/document/csv/dummy.csv",
            file_type = "csv",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_txt_url_valid():
    n_questions = 1

    quiz = executor(
        topic = "college",
        n_questions = n_questions,
        file_url = "https://filesamples.com/samples/document/txt/sample1.txt",
        file_type = "txt",
        lang = "en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_txt_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://filesamples.com/samples/document/txt/dummy.txt",
            file_type = "txt",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_md_url_valid():
    n_questions = 1

    quiz = executor(
        topic = "college",
        n_questions = n_questions,
        file_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        file_type = "md",
        lang = "en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_md_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/dummy.md",
            file_type = "md",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_pptx_url_valid():
    n_questions = 1

    quiz = executor(
        topic = "college",
        n_questions = 1,
        file_url = "https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        file_type = "pptx",
        lang = "en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_pptx_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://filesamples.com/samples/document/samplepptx.pptx",
            file_type = "pptx",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_docx_url_valid():

    n_questions = 1

    quiz = executor(
        topic = "college",
        n_questions = n_questions,
        file_url = "https://filesamples.com/samples/document/docx/sample1.docx",
        file_type = "docx",
        lang = "en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_docx_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://filesamples.com/samples/document/docx/dummy.docx",
            file_type = "docx",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_xls_url_valid():

    n_questions = 1

    quiz = executor(
        topic = "college",
        n_questions = n_questions,
        file_url = "https://filesamples.com/samples/document/xls/sample1.xls",
        file_type = "xls",
        lang = "en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_xls_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://filesamples.com/samples/document/xls/dummy.xls",
            file_type = "xls",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_xlsx_url_valid():
    n_questions = 1

    quiz = executor(
        topic = "college",
        n_questions = n_questions,
        file_url = "https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        file_type = "xlsx",
        lang = "en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_xlsx_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://filesamples.com/samples/document/xlsx/dummy.xlsx",
            file_type = "xlsx",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_xml_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://filesampleshub.com/download/code/xml/dummy.xml",
            file_type = "xml",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_gdocs_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit",
            file_type = "gdoc",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_gsheets_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type = "gsheet",
            lang = "en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_gslides_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type = "gslide",
            lang="en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_gpdfs_url_valid():
    n_questions = 1

    quiz = executor(
        topic = "doc",
        n_questions = n_questions,
        file_url = "https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        file_type = "gpdf",
        lang="en",
        grade_level= "college",
        quiz_description= "Test quiz"
    )

    assert isinstance(quiz, list)
    assert len(quiz) == n_questions

def test_executor_gpdfs_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://drive.google.com/file/d/1gBeAzJKTaZFwEbub8wkXrF3/view?usp=sharing",
            file_type = "gpdf",
            lang="en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_mp3_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = "a",
            file_url = "https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            file_type = "mp3",
            lang="en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)

def test_executor_gmp3_url_invalid():

    with pytest.raises(ValueError) as exc_info:
        quiz = executor(
            topic = "college",
            n_questions = 1,
            file_url = "https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            file_type = "gmp3",
            lang="en",
            grade_level= "college",
            quiz_description= "Test quiz"
        )

    assert isinstance(exc_info.value, ValueError)
def test_quiz_voting():
    n_questions = 1
    quiz = executor(
        topic="test topic",
        n_questions=n_questions,
        file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type="pdf",
        lang="en"
    )
    
    assert isinstance(quiz[0].get('thumbs_up', 0), int)
    assert isinstance(quiz[0].get('thumbs_down', 0), int)
def test_vocabulary_quiz():
    n_questions = 10
    quiz = executor(
        topic="Science Terms Vocabulary",
        n_questions=n_questions,
        file_url="attached_assets/Science_Glossary.pdf",
        file_type="pdf",
        lang="en"
    )
    
    assert isinstance(quiz, list)
    assert len(quiz) == n_questions
    # Check if questions contain vocabulary-related content
    for question in quiz:
        assert 'question' in question
        assert 'choices' in question
        assert 'answer' in question
        assert 'explanation' in question
        assert isinstance(question.get('thumbs_up', 0), int)
        assert isinstance(question.get('thumbs_down', 0), int)
