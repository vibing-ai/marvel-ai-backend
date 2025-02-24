import pytest
from app.api.error_utilities import SyllabusGeneratorError
from app.tools.syllabus_generator.core import executor
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

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

# Test 1: Basic functionality with PDF
def test_executor_pdf_url_valid():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type="pdf"
    )
    assert isinstance(syllabus, dict)
    # Check all expected sections are present
    expected_sections = [
        "course_information", "learning_outcomes", "course_content",
        "assessment_criteria", "course_schedule", "learning_resources",
        "policies_procedures"
    ]
    for section in expected_sections:
        assert section in syllabus, f"Missing section: {section}"
    # Basic content check
    assert "arithmetic" in syllabus["course_information"].lower(), "Course info should mention arithmetic"

# Test 2: Default values for new fields
def test_executor_with_defaults():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt"
    )
    assert isinstance(syllabus, dict)
    assert "course_schedule" in syllabus
    # Validate defaults in course_schedule
    schedule_str = str(syllabus["course_schedule"]).lower()
    assert "week" in schedule_str, "Should use default unit_time 'Week'"
    assert "2025-03-01" in schedule_str, "Should use default start_date '2025-03-01'"
    # Check learning outcomes (5-7 expected)
    assert "learning_outcomes" in syllabus
    outcomes = syllabus["learning_outcomes"]
    assert isinstance(outcomes, list) and 5 <= len(outcomes) <= 7, "Should have 5-7 outcomes"

# Test 3: Custom values for new fields
def test_executor_with_custom_time():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt",
        unit_time="Day",
        unit_time_value=5,
        start_date="2025-04-01"
    )
    assert isinstance(syllabus, dict)
    assert "course_schedule" in syllabus
    # Validate custom values in course_schedule
    schedule_str = str(syllabus["course_schedule"]).lower()
    assert "day" in schedule_str, "Should reflect custom unit_time 'Day'"
    assert "2025-04-01" in schedule_str, "Should reflect custom start_date '2025-04-01'"
    # Check course_content reflects unit_time_value
    content_str = str(syllabus["course_content"]).lower()
    assert len(syllabus["course_content"]) <= 5, "Course content should respect unit_time_value of 5"

# Test 4: Dependency check (objectives influencing learning_outcomes)
def test_executor_objectives_dependency():
    syllabus = executor(
        **base_attributes,
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt",
        objectives="Master addition; Understand fractions"
    )
    assert "learning_outcomes" in syllabus
    outcomes_str = str(syllabus["learning_outcomes"]).lower()
    assert "addition" in outcomes_str, "Learning outcomes should reflect objectives"
    # Note: This assumes you enhanced learning_outcomes_prompt to use {objectives}

# Test 5: Minimal input with defaults
def test_executor_minimal_input():
    minimal_attributes = {
        "grade_level": "6th grade",
        "subject": "Science",
        "course_description": "Intro to biology",
        "objectives": "Learn basics",
        "required_materials": "Textbook",
        "grading_policy": "50% tests",
        "policies_expectations": "Attend class",
        "course_outline": "Week 1: Cells",
        "additional_notes": "",
        "lang": "en",
        "file_url": "https://filesamples.com/samples/document/txt/sample1.txt",
        "file_type": "txt"
    }
    syllabus = executor(**minimal_attributes)
    assert isinstance(syllabus, dict)
    assert all(section in syllabus for section in [
        "course_information", "course_schedule"
    ]), "Should generate all sections with minimal input"

# Test 6: Error handling for invalid file_type
def test_executor_invalid_file_type():
    with pytest.raises(SyllabusGeneratorError):
        executor(
            **base_attributes,
            file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            file_type="invalid_type"
        )