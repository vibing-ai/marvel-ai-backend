import pytest
from app.features.syllabus_generator.core import executor
from app.api.error_utilities import SyllabusGeneratorError
from app.services.schemas import SyllabusGeneratorArgsModel

def test_executor_pdf_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type = "pdf"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_pdf_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/pdf/dummy.pdf",
        file_type = "pdf"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)


def test_executor_csv_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/csv/sample1.csv",
        file_type = "csv"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_csv_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/csv/dummy.csv",
        file_type = "csv"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)

def test_executor_txt_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/txt/sample1.txt",
        file_type = "txt"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_txt_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/txt/dummy.txt",
        file_type = "txt"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)


def test_executor_md_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        file_type = "md"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_md_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://github.com/radicalxdev/kai-ai-backend/blob/main/dummy.md",
        file_type = "md"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)


def test_executor_pptx_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        file_type = "pptx"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_pptx_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://scholar.harvard.edu/files/torman_personal/files/dummy.pptx",
        file_type = "pptx"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)


def test_executor_docx_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/docx/sample1.docx",
        file_type = "docx"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_docx_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/docx/dummy.docx",
        file_type = "docx"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)

def test_executor_xls_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/xls/sample1.xls",
        file_type = "xls"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_xls_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/xls/dummy.xls",
        file_type = "xls"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)

def test_executor_xlsx_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        file_type = "xlsx"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_xlsx_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesamples.com/samples/document/xlsx/dummy.xlsx",
        file_type = "xlsx"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)

def test_executor_xml_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesampleshub.com/download/code/xml/sample1.xml",
        file_type = "xml"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_xml_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://filesampleshub.com/download/code/xml/dummy.xml",
        file_type = "xml"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)

def test_executor_gdocs_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://docs.google.com/document/d/1kBzpRJYrD8KgOu0i_ATDk9TDtrDoxO-3wpm14_BGMGw/edit",
        file_type = "gdoc"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_gdocs_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit",
        file_type = "gdoc"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)

def test_executor_gsheets_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://docs.google.com/spreadsheets/d/1TTSFMXTxW_JhZ4T-K_vU3hXqWaIYwlP_X69jEiVL0KQ/edit",
        file_type = "gsheet"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_gsheets_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
        file_type = "gsheet"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)

def test_executor_gslides_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://docs.google.com/presentation/d/16b6wQUyKJUOmwSgiuhUarB7tr5rgJ0TDJoSrnzIaIfA/edit",
        file_type = "gslide"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_gslides_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://docs.google.com/presentation/d/1GeIRGJF63v683LEn4J3UnhI/edit",
        file_type = "gslide"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)

def test_executor_gpdfs_url_valid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        file_type = "gpdf"
    )

    syllabus = executor(syllabus_generator_args)
    
    assert isinstance(syllabus, dict)
    assert len(syllabus) > 0

def test_executor_gpdfs_url_invalid():
    syllabus_generator_args = SyllabusGeneratorArgsModel(
        grade_level = "college",
        course = "Advanced Data Structures",
        instructor_name = "Radical AI",
        instructor_title = "PhD in CS",
        unit_time = "week",
        unit_time_value = 8,
        start_date = "July, 4th, 2024",
        assessment_methods = "project and exams",
        grading_scale = "In percentages (100%)",
        file_url = "https://drive.google.com/file/d/1gBeAzJKTaZFwEbub8wkXrF3/view?usp=sharing",
        file_type = "gpdf"
    )

    with pytest.raises(SyllabusGeneratorError) as exc_info:
        syllabus = executor(syllabus_generator_args)

    assert isinstance(exc_info.value, SyllabusGeneratorError)