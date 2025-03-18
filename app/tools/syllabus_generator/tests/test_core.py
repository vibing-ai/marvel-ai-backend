import pytest
from unittest.mock import patch, MagicMock
from app.api.error_utilities import SyllabusGeneratorError
from app.tools.syllabus_generator.core import executor
from app.services.schemas import SyllabusGeneratorArgsModel
from app.tools.syllabus_generator.tools import (
    SyllabusRequestArgs,
    SyllabusGeneratorPipeline,
    SyllabusGenerator,
    CompilePipelineError,
)

from langchain_core.runnables import RunnableParallel
from fastapi import HTTPException

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
    "lang": "en",
    "file_url": "",
    "file_type": ""
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
            file_type="a"
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
            file_type="a"
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
            file_type="a"
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
            file_type="a"
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
            file_type="a"
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# XML Tests
def test_executor_xml_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://filesampleshub.com/download/code/xml/dummy.xml",
            file_type="a"
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# GDocs Tests
def test_executor_gdocs_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit",
            file_type="a"
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# GSheets Tests
def test_executor_gsheets_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type="a"
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# GSlides Tests
def test_executor_gslides_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type="a"
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
            file_type="a"
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)

# MP3 Tests
def test_executor_mp3_url_invalid():
    with pytest.raises(SyllabusGeneratorError) as exc_info:
        executor(
            **base_attributes,
            file_url="https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            file_type="a"
        )
    assert isinstance(exc_info.value, SyllabusGeneratorError)


# Test for SyllabusRequestArgs class
def test_syllabus_request_args():
    # Create a mock SyllabusGeneratorArgsModel object
    mock_args = MagicMock(spec=SyllabusGeneratorArgsModel)
    for key, value in base_attributes.items():
        setattr(mock_args, key, value)
    
    # Test initialization and to_dict method
    request_args = SyllabusRequestArgs(mock_args, "Test summary")
    args_dict = request_args.to_dict()
    
    assert args_dict["grade_level"] == "5th grade"
    assert args_dict["subject"] == "Math"
    assert args_dict["summary"] == "Test summary"
    assert "course_description" in args_dict
    assert "objectives" in args_dict

# Test the pipeline compilation
@patch('app.tools.syllabus_generator.tools.GoogleGenerativeAI')
def test_pipeline_compile(mock_model):
    # Setup mock model
    mock_model_instance = MagicMock()
    mock_model.return_value = mock_model_instance
    
    # Create SyllabusGeneratorPipeline and test if it compiles without errors
    pipeline = SyllabusGeneratorPipeline(verbose=True)
    runnables = pipeline.compile()
    
    # Verify the runnables were created
    assert isinstance(runnables, list)
    assert len(runnables) == 3  # We expect three parallel runnables
    
    # Verify each runnable is a RunnableParallel
    for runnable in runnables:
        assert isinstance(runnable, RunnableParallel)
    
    # Verify the steps were created
    assert hasattr(pipeline, 'steps')
    required_sections = [
        "course_information",
        "course_description_objectives",
        "course_content",
        "policies_procedures",
        "assessment_grading_criteria",
        "learning_resources",
        "course_schedule"
    ]
    
    for section in required_sections:
        assert section in pipeline.steps
        assert hasattr(pipeline.steps[section], 'chain')
        assert pipeline.steps[section].chain is not None

@patch('app.tools.syllabus_generator.tools.SyllabusGeneratorPipeline')
def test_generate_syllabus(mock_pipeline_class):
    # Create mock objects
    mock_pipeline = MagicMock()
    mock_pipeline_class.return_value = mock_pipeline
    
    # Setup runnables with correct structure and step names
    mock_runnable1 = MagicMock(spec=RunnableParallel)
    
    mock_runnable2 = MagicMock()
    mock_runnable2.config = MagicMock()
    mock_runnable2.config.get.return_value = "course_content"
    
    mock_runnable3 = MagicMock()
    mock_runnable3.config = MagicMock()
    mock_runnable3.config.get.return_value = "assessment_grading_criteria"
    
    mock_runnable4 = MagicMock()
    mock_runnable4.config = MagicMock()
    mock_runnable4.config.get.return_value = "policies_procedures"
    
    mock_runnable5 = MagicMock()
    mock_runnable5.config = MagicMock()
    mock_runnable5.config.get.return_value = "learning_resources"
    
    mock_runnable6 = MagicMock()
    mock_runnable6.config = MagicMock()
    mock_runnable6.config.get.return_value = "course_schedule"
    
    # Set up mock return values for RunnableParallel
    parallel_results = {
        "course_information": {
            "course_title": "Math 101",
            "grade_level": "5th grade",
            "description": "This course covers basic arithmetic operations."
        },
        "course_description_objectives": {
            "objectives": ["Learn addition", "Master multiplication"],
            "intended_learning_outcomes": ["Can add numbers", "Can multiply numbers"]
        }
    }
    mock_runnable1.invoke.return_value = parallel_results
    
    # Set up return values for sequential runnables
    mock_runnable2.invoke.return_value = [
        {
            "unit_sequence": 1,
            "title": "Addition",
            "description": "Basic addition",
            "key_topics": ["Single digit addition", "Double digit addition"],
            "learning_outcomes": ["Can add single digits", "Can add double digits"]
        }
    ]
    
    mock_runnable3.invoke.return_value = {
        "assessment_methods": [
            {
                "type_assessment": "Exam",
                "weight": 60
            }
        ],
        "grading_scale": {
            "A": "90-100",
            "B": "80-89",
            "C": "70-79",
            "D": "60-69",
            "F": "0-59"
        }
    }
    
    mock_runnable4.invoke.return_value = {
        "attendance_policy": "Mandatory",
        "late_submission_policy": "Penalties apply",
        "academic_honesty": "Required"
    }
    
    mock_runnable5.invoke.return_value = [
        {
            "title": "Math Book",
            "author": "John Doe",
            "year": 2023
        }
    ]
    
    mock_runnable6.invoke.return_value = [
        {
            "session_number": 1,
            "date": "2024-01-01",
            "time_frame": "1 week",
            "topic": "Addition",
            "activity_desc": "Practice problems"
        }
    ]
    
    # Mock the compile method to return the mock runnables
    mock_pipeline.compile.return_value = [
        mock_runnable1,
        mock_runnable2,
        mock_runnable3,
        mock_runnable4,
        mock_runnable5,
        mock_runnable6
    ]
    
    # Create a mock SyllabusGeneratorArgsModel object
    mock_args = MagicMock(spec=SyllabusGeneratorArgsModel)
    for key, value in base_attributes.items():
        setattr(mock_args, key, value)
    
    # Create SyllabusRequestArgs and mock its to_dict method
    request_args = MagicMock(spec=SyllabusRequestArgs)
    request_dict = {"course_title": None, "grade_level": None, "summary": "Test summary"}
    request_args.to_dict.return_value = request_dict
    
    # Mock the trace context manager
    mock_trace = MagicMock()
    mock_trace.__enter__ = MagicMock(return_value=MagicMock())
    mock_trace.__exit__ = MagicMock(return_value=None)
    
    # Mock the _validate_output method and langsmith trace
    with patch('app.tools.syllabus_generator.tools.SyllabusGenerator._validate_output', return_value={}), \
         patch('langsmith.trace', return_value=mock_trace):
        # Create SyllabusGenerator instance
        generator = SyllabusGenerator(verbose=True)
        
        # Test generate_syllabus
        result = generator.generate_syllabus(request_args, verbose=True)
    
    # Assertions
    assert isinstance(result, dict)
    assert "course_information" in result
    assert "course_description_objectives" in result
    assert "course_content" in result
    assert "policies_procedures" in result
    assert "assessment_grading_criteria" in result
    assert "learning_resources" in result
    assert "course_schedule" in result
    
    # Verify the correct methods were called
    mock_pipeline.compile.assert_called_once()
    mock_runnable1.invoke.assert_called_once()
    mock_runnable2.invoke.assert_called_once()
    mock_runnable3.invoke.assert_called_once()
    mock_runnable4.invoke.assert_called_once()
    mock_runnable5.invoke.assert_called_once()
    mock_runnable6.invoke.assert_called_once()

# Test error handling in generate_syllabus
@patch('app.tools.syllabus_generator.tools.SyllabusGeneratorPipeline')
def test_generate_syllabus_error_handling(mock_pipeline_class):
    # Make the pipeline raise an exception
    mock_pipeline = MagicMock()
    mock_pipeline_class.return_value = mock_pipeline
    mock_pipeline.compile.side_effect = CompilePipelineError("Test error")
    
    # Create a mock SyllabusGeneratorArgsModel object
    mock_args = MagicMock(spec=SyllabusGeneratorArgsModel)
    for key, value in base_attributes.items():
        setattr(mock_args, key, value)
    
    # Create SyllabusRequestArgs
    request_args = SyllabusRequestArgs(mock_args, "Test summary")
    
    # Create SyllabusGenerator instance
    generator = SyllabusGenerator(verbose=True)
    
    # Test that it raises HTTPException
    with pytest.raises(HTTPException) as exc_info:
        generator.generate_syllabus(request_args, verbose=True)
    
    assert exc_info.value.status_code == 500
    assert "Failed to generate syllabus from LLM" in str(exc_info.value.detail)

# Integration test combining existing executor with new pipeline
@patch('app.tools.syllabus_generator.tools.SyllabusGenerator.generate_syllabus')
def test_integration_executor_with_pipeline(mock_generate_syllabus):
    # Mock the generate_syllabus function to return a simple dict
    mock_generate_syllabus.return_value = {
        "course_information": {"course_title": "Math 101"},
        "course_description_objectives": {"objectives": ["Learn math"]},
        "course_content": [{"unit_sequence": 1, "title": "Addition", "description": "Basic addition", "key_topics": ["Single digit addition"], "learning_outcomes": ["Can add single digits"]}],
        "policies_procedures": {"attendance_policy": "Mandatory"},
        "assessment_grading_criteria": {"grading_scale": {"A": "90-100"}},
        "learning_resources": [{"title": "Math Book"}],
        "course_schedule": [{"session_number": 1, "date": "2024-01-01", "time_frame": "1 week", "topic": "Addition", "activity_desc": "Practice problems"}]
    }
    
    # Test executor with no file (should use pipeline directly)
    result = executor(**base_attributes)
    assert isinstance(result, dict)
    assert "course_information" in result
    assert "course_description_objectives" in result
    assert "course_content" in result
    assert "policies_procedures" in result
    assert "assessment_grading_criteria" in result
    assert "learning_resources" in result
    assert "course_schedule" in result
    
    # Verify generate_syllabus was called
    mock_generate_syllabus.assert_called_once()