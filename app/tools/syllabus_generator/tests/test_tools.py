import pytest
from unittest.mock import patch, MagicMock
from app.tools.syllabus_generator.tools import (
    SyllabusGeneratorPipeline, 
    CompilePipelineError, 
    ChainBuilder, 
    resume_course_content, 
    PromptFactory, 
    ParserFactory, 
    SyllabusGenerator, 
    SyllabusRequestArgs, 
    SyllabusGeneratorArgsModel, 
    OutputValidationError,
    PipelineStep
)
from langchain_core.runnables import RunnableLambda, Runnable
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai.llms import GoogleGenerativeAI
import json
import concurrent.futures

# Fixtures
@pytest.fixture
def pipeline():
    return SyllabusGeneratorPipeline(model_name="gemini-1.5-pro", model_max_retries=3, verbose=False)

@pytest.fixture
def parsers():
    return ParserFactory.create_parsers()

@pytest.fixture
def chain_builder(parsers, pipeline):
    return ChainBuilder(pipeline.model, parsers, verbose=False)

@pytest.fixture
def fallbacks_list(chain_builder):
    return chain_builder.create_fallback("test_section")

@pytest.fixture
def runnables(pipeline):
    return pipeline.compile()

@pytest.fixture
def steps(runnables, pipeline):
    return pipeline.steps

@pytest.fixture
def fallback(fallbacks_list):
    return fallbacks_list[0]

@pytest.fixture
def sample_syllabus_args():
    return SyllabusGeneratorArgsModel(
        grade_level="High School",
        subject="Mathematics",
        course_description="Introduction to Algebra",
        objectives="Learn basic algebraic concepts",
        required_materials="Textbook, calculator",
        grading_policy="Standard grading scale",
        policies_expectations="Regular attendance required",
        course_outline="Basic algebra concepts",
        additional_notes="None",
        lang="en",
        file_url="",
        file_type=""
    )

@pytest.fixture
def sample_summary():
    return "This is a sample course summary"

@pytest.fixture
def syllabus_request_args(sample_syllabus_args, sample_summary):
    return SyllabusRequestArgs(sample_syllabus_args, sample_summary)

# Test PipelineStep
class TestPipelineStep:
    """Test suite for PipelineStep class functionality."""
    
    def test_initialization(self):
        """Test PipelineStep initialization with different execution modes."""
        step = PipelineStep(
            name="test_step",
            prompt_factory=PromptFactory.course_information,
            parser_key="course_information",
            dependencies=["dep1", "dep2"],
            execution_mode="sequential"
        )
        assert step.name == "test_step"
        assert step.dependencies == ["dep1", "dep2"]
        assert step.execution_mode == "sequential"

    def test_default_values(self):
        """Test PipelineStep initialization with default values."""
        step = PipelineStep(
            name="test_step",
            prompt_factory=PromptFactory.course_information,
            parser_key="course_information"
        )
        assert step.dependencies == []
        assert step.execution_mode == "sequential"

# Test ChainBuilder
class TestChainBuilder:
    """Test suite for ChainBuilder functionality."""
    
    def test_basic_functionality(self, chain_builder):
        """Test ChainBuilder basic functionality."""
        prompt = PromptFactory.course_information("Format as JSON")
        chain = chain_builder.build_chain_with_fallback(
            prompt=prompt,
            section_name="test_section",
            parser_key="course_information"
        )
        assert isinstance(chain, Runnable)
        assert hasattr(chain, "invoke")

    def test_chain_execution_modes(self, steps):
        """Test that chains are properly configured for their execution modes."""
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
            assert section in steps, f"Missing section: {section}"
            chain = steps[section].chain
            assert hasattr(chain, 'invoke'), f"Chain {section} is not invokable"
            assert hasattr(chain, 'fallbacks'), f"Chain {section} has no fallbacks"
            assert len(chain.fallbacks) > 0, f"Chain {section} has empty fallbacks"

    def test_chain_with_fallback_integration(self, fallbacks_list):
        """Test the fallback integration with a chain that fails."""
        def failing_function(input_data: dict, *args, **kwargs):
            raise ValueError("Simulated failure")
        
        failing_chain = RunnableLambda(failing_function)
        chain_with_fallback = failing_chain.with_fallbacks(fallbacks_list, exception_key = "error")
        
        result = chain_with_fallback.invoke({"query": "Test input"})
        
        assert result["status"] == "failed"
        assert result["section"] == "test_section"
        assert result["fallback"] is True
        assert result["error"] == "Simulated failure"

# Test SyllabusRequestArgs
class TestSyllabusRequestArgs:
    """Test suite for SyllabusRequestArgs functionality."""
    
    def test_initialization(self, syllabus_request_args):
        """Test the initialization of SyllabusRequestArgs with default values."""
        assert syllabus_request_args._grade_level == "High School"
        assert syllabus_request_args._subject == "Mathematics"
        assert syllabus_request_args._course_description == "Introduction to Algebra"
        assert syllabus_request_args._objectives == "Learn basic algebraic concepts"
        assert syllabus_request_args._required_materials == "Textbook, calculator"
        assert syllabus_request_args._grading_policy == "Standard grading scale"
        assert syllabus_request_args._policies_expectations == "Regular attendance required"
        assert syllabus_request_args._course_outline == "Basic algebra concepts"
        assert syllabus_request_args._additional_notes == "None"
        assert syllabus_request_args._lang == "en"
        assert syllabus_request_args._summary == "This is a sample course summary"

    def test_to_dict(self, syllabus_request_args):
        """Test the to_dict method of SyllabusRequestArgs."""
        result = syllabus_request_args.to_dict()
        assert isinstance(result, dict)
        assert result["grade_level"] == "High School"
        assert result["subject"] == "Mathematics"
        assert result["course_description"] == "Introduction to Algebra"
        assert result["objectives"] == "Learn basic algebraic concepts"
        assert result["required_materials"] == "Textbook, calculator"
        assert result["grading_policy"] == "Standard grading scale"
        assert result["policies_expectations"] == "Regular attendance required"
        assert result["course_outline"] == "Basic algebra concepts"
        assert result["additional_notes"] == "None"
        assert result["lang"] == "en"
        assert result["summary"] == "This is a sample course summary"

# Test PromptFactory
class TestPromptFactory:
    """Test suite for PromptFactory class."""
    
    @pytest.fixture
    def parser_instructions(self):
        return "Format as JSON"

    def test_course_information_prompt(self, parser_instructions):
        """Test course_information prompt factory."""
        prompt = PromptFactory.course_information(parser_instructions)
        assert isinstance(prompt, PromptTemplate)
        assert all(var in prompt.input_variables for var in [
            "grade_level", "subject", "course_description", "lang",
            "summary", "additional_notes"
        ])
        assert "format_instructions" in prompt.partial_variables
        assert prompt.partial_variables["format_instructions"] == parser_instructions

    def test_course_description_objectives_prompt(self, parser_instructions):
        """Test course_description_objectives prompt factory."""
        prompt = PromptFactory.course_description_objectives(parser_instructions)
        assert isinstance(prompt, PromptTemplate)
        assert all(var in prompt.input_variables for var in [
            "objectives", "lang", "summary", "grade_level",
            "subject", "course_description"
        ])
        assert "format_instructions" in prompt.partial_variables
        assert prompt.partial_variables["format_instructions"] == parser_instructions

    def test_course_content_prompt(self, parser_instructions):
        """Test course_content prompt factory."""
        prompt = PromptFactory.course_content(parser_instructions)
        assert isinstance(prompt, PromptTemplate)
        assert all(var in prompt.input_variables for var in [
            "course_information", "course_outline", "lang", "summary", "course_objectives"
        ])

    def test_policies_procedures_prompt(self, parser_instructions):
        """Test policies_procedures prompt factory."""
        prompt = PromptFactory.policies_procedures(parser_instructions)
        assert isinstance(prompt, PromptTemplate)
        assert all(var in prompt.input_variables for var in [
            "grading_policy", "policies_expectations", "lang", "grade_level", "course_title"
        ])
        assert "format_instructions" in prompt.partial_variables
        assert prompt.partial_variables["format_instructions"] == parser_instructions

    def test_assessment_grading_criteria_prompt(self, parser_instructions):
        """Test assessment_grading_criteria prompt factory."""
        prompt = PromptFactory.assessment_grading_criteria(parser_instructions)
        assert isinstance(prompt, PromptTemplate)
        assert all(var in prompt.input_variables for var in [
            "grading_policy", "lang", "course_title", "grade_level", "course_objectives"
        ])
        assert "format_instructions" in prompt.partial_variables
        assert prompt.partial_variables["format_instructions"] == parser_instructions

    def test_learning_resources_prompt(self, parser_instructions):
        """Test learning_resources prompt factory."""
        prompt = PromptFactory.learning_resources(parser_instructions)
        assert isinstance(prompt, PromptTemplate)
        assert all(var in prompt.input_variables for var in [
            "required_materials", "lang", "course_title", "subject", "grade_level"
        ])
        assert "format_instructions" in prompt.partial_variables
        assert prompt.partial_variables["format_instructions"] == parser_instructions

    def test_course_schedule_prompt(self, parser_instructions):
        """Test course_schedule prompt factory."""
        prompt = PromptFactory.course_schedule(parser_instructions)
        assert isinstance(prompt, PromptTemplate)
        assert all(var in prompt.input_variables for var in [
            "course_title", "grade_level", "course_content", "lang"
        ])

    def test_prompt_template_content(self, parser_instructions):
        """Test that all prompts contain the expected template content."""
        prompts = [
            (PromptFactory.course_information, "curriculum designer"),
            (PromptFactory.course_description_objectives, "learning outcomes"),
            (PromptFactory.course_content, "course content outline"),
            (PromptFactory.policies_procedures, "educational policies"),
            (PromptFactory.assessment_grading_criteria, "assessment methods"),
            (PromptFactory.learning_resources, "learning materials"),
            (PromptFactory.course_schedule, "course schedule")
        ]

        for factory_method, expected_content in prompts:
            prompt = factory_method(parser_instructions)
            assert expected_content in prompt.template.lower()

    def test_prompt_format_instructions(self, parser_instructions):
        """Test that format instructions are properly included in all prompts."""
        prompt_methods = [
            PromptFactory.course_information,
            PromptFactory.course_description_objectives,
            PromptFactory.course_content,
            PromptFactory.policies_procedures,
            PromptFactory.assessment_grading_criteria,
            PromptFactory.learning_resources,
            PromptFactory.course_schedule
        ]

        for method in prompt_methods:
            if method == PromptFactory.course_content or method == PromptFactory.course_schedule:
                continue
            prompt = method(parser_instructions)
            assert "{format_instructions}" in prompt.template
            assert prompt.partial_variables["format_instructions"] == parser_instructions

    def test_prompt_language_support(self, parser_instructions):
        """Test that all prompts support language specification."""
        prompt_methods = [
            PromptFactory.course_information,
            PromptFactory.course_description_objectives,
            PromptFactory.course_content,
            PromptFactory.policies_procedures,
            PromptFactory.assessment_grading_criteria,
            PromptFactory.learning_resources,
            PromptFactory.course_schedule
        ]

        for method in prompt_methods:
            prompt = method(parser_instructions)
            assert "lang" in prompt.input_variables
            assert "{lang}" in prompt.template

    def test_prompt_grade_level_support(self, parser_instructions):
        """Test that all prompts support grade level specification."""
        prompt_methods = [
            PromptFactory.course_information,
            PromptFactory.course_description_objectives,
            PromptFactory.course_content,
            PromptFactory.policies_procedures,
            PromptFactory.assessment_grading_criteria,
            PromptFactory.learning_resources,
            PromptFactory.course_schedule
        ]

        for method in prompt_methods:
            prompt = method(parser_instructions)
            assert "grade_level" in prompt.input_variables
            assert "{grade_level}" in prompt.template

# Test ParserFactory
class TestParserFactory:
    """Test suite for ParserFactory class."""
    
    def test_create_parsers_returns_dict(self):
        """Test that create_parsers returns a dictionary of parsers."""
        parsers = ParserFactory.create_parsers()
        assert isinstance(parsers, dict)
        assert len(parsers) > 0

    def test_parser_types(self):
        """Test that all parsers are JsonOutputParser instances."""
        parsers = ParserFactory.create_parsers()
        for parser in parsers.values():
            assert isinstance(parser, JsonOutputParser)

    def test_required_parsers_exist(self):
        """Test that all required parsers are created."""
        parsers = ParserFactory.create_parsers()
        required_parsers = [
            "course_information",
            "course_description_objectives",
            "course_content",
            "policies_procedures",
            "assessment_grading_criteria",
            "learning_resources",
            "course_schedule"
        ]
        for parser_name in required_parsers:
            assert parser_name in parsers

    def test_parser_schema_validation(self):
        """Test that parsers validate against their expected schemas."""
        parsers = ParserFactory.create_parsers()
        
        # Test course information parser
        course_info_parser = parsers["course_information"]
        valid_course_info = {
            "title": "Test Course",
            "grade_level": "High School",
            "subject": "Mathematics",
            "description": "Test Description"
        }
        assert course_info_parser.parse(json.dumps(valid_course_info)) == valid_course_info

        # Test course description objectives parser
        objectives_parser = parsers["course_description_objectives"]
        valid_objectives = {
            "objectives": ["Objective 1", "Objective 2"],
            "learning_outcomes": ["Outcome 1", "Outcome 2"]
        }
        assert objectives_parser.parse(json.dumps(valid_objectives)) == valid_objectives

        # Test course content parser
        content_parser = parsers["course_content"]
        valid_content = {
            "units": [
                {
                    "title": "Unit 1",
                    "duration": "2 weeks",
                    "topics": ["Topic 1", "Topic 2"]
                }
            ]
        }
        assert content_parser.parse(json.dumps(valid_content)) == valid_content

    def test_parser_error_handling(self):
        """Test that parsers handle invalid input appropriately."""
        parsers = ParserFactory.create_parsers()
        
        # Test with invalid JSON
        invalid_json = "not a json"
        for parser_name, parser in parsers.items():
            with pytest.raises(Exception) as exc_info:
                parser.parse(invalid_json)
            assert "Invalid json output" in str(exc_info.value)

        # Test with valid JSON but missing fields
        # Note: JsonOutputParser doesn't validate schema, so this should pass
        invalid_course_info = {
            "title": "Test Course"
            # Missing required fields
        }
        result = parsers["course_information"].parse(json.dumps(invalid_course_info))
        assert result == invalid_course_info

        # Test with valid JSON but invalid field types
        # Note: JsonOutputParser doesn't validate types, so this should pass
        invalid_types = {
            "course_information": {
                "title": 123,  # Should be string
                "grade_level": ["High School"],  # Should be string
                "subject": None,  # Should be string
                "description": True  # Should be string
            }
        }
        result = parsers["course_information"].parse(json.dumps(invalid_types))
        assert result == invalid_types

        # Test with valid JSON but malformed structure
        # Note: JsonOutputParser doesn't validate structure, so this should pass
        malformed_nested = {
            "course_content": {
                "units": "not a list"  # Should be a list
            }
        }
        result = parsers["course_content"].parse(json.dumps(malformed_nested))
        assert result == malformed_nested

        # Test with valid JSON but empty fields
        # Note: JsonOutputParser doesn't validate content, so this should pass
        empty_fields = {
            "course_information": {
                "title": "",
                "grade_level": "",
                "subject": "",
                "description": ""
            }
        }
        result = parsers["course_information"].parse(json.dumps(empty_fields))
        assert result == empty_fields

# Test SyllabusGenerator
class TestSyllabusGenerator:
    """Test suite for SyllabusGenerator class."""
    
    def test_validate_output(self):
        """Test the output validation functionality."""
        generator = SyllabusGenerator(error_threshold=0.8)
        
        # Test successful validation
        valid_output = {
            "course_information": {"title": "Test Course"},
            "course_description_objectives": {"objectives": ["Objective 1"]},
            "course_content": {"content": ["Content 1"]},
            "policies_procedures": {"policies": ["Policy 1"]},
            "assessment_grading_criteria": {"criteria": ["Criterion 1"]},
            "learning_resources": {"resources": ["Resource 1"]},
            "course_schedule": {"schedule": ["Schedule 1"]}
        }
        
        metadata = generator._validate_output(valid_output)
        assert metadata["status"] == "success"
        assert metadata["error_rate"] == 0
        assert not metadata["error_sections"]
        
        # Test partial failure
        partial_output = {
            "course_information": {"error": "Failed"},
            "course_description_objectives": {"objectives": ["Objective 1"]},
            "course_content": {"content": ["Content 1"]},
            "policies_procedures": {"policies": ["Policy 1"]},
            "assessment_grading_criteria": {"criteria": ["Criterion 1"]},
            "learning_resources": {"resources": ["Resource 1"]},
            "course_schedule": {"schedule": ["Schedule 1"]}
        }
        
        metadata = generator._validate_output(partial_output)
        assert metadata["status"] == "partial_success"
        assert metadata["error_rate"] == 0.14  # 1/7 sections failed
        assert "course_information" in metadata["error_sections"]
        
        # Test complete failure
        failed_output = {
            "course_information": {"error": "Failed"},
            "course_description_objectives": {"error": "Failed"},
            "course_content": {"error": "Failed"},
            "policies_procedures": {"error": "Failed"},
            "assessment_grading_criteria": {"error": "Failed"},
            "learning_resources": {"error": "Failed"},
            "course_schedule": {"error": "Failed"}
        }
        
        with pytest.raises(OutputValidationError) as exc_info:
            generator._validate_output(failed_output) 
        assert str(exc_info.value) == "Failed to generate any section."

# Test Pipeline Compilation
class TestPipelineCompilation:
    """Test suite for pipeline compilation functionality."""
    
    def test_compile_returns_dict_with_correct_keys(self, steps):
        """Test that compile returns a dictionary with all required sections."""
        required_sections = [
            "course_information",
            "course_description_objectives",
            "course_content",
            "policies_procedures",
            "assessment_grading_criteria",
            "learning_resources",
            "course_schedule"
        ]
        
        assert isinstance(steps, dict)
        for section in required_sections:
            assert section in steps, f"Missing required section: {section}"

    def test_compile_steps_structure(self, steps):
        """Test that compile returns chains with correct structure."""
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
            assert section in steps, f"Missing chain: {section}"
            chain = steps[section].chain
            assert hasattr(chain, "invoke"), f"{section} is not a runnable"
            assert hasattr(chain, "fallbacks"), f"{section} has no fallbacks"
            assert len(chain.fallbacks) > 0, f"{section} has empty fallbacks"

    def test_compile_handles_errors(self, pipeline):
        """Test that compile handles errors properly."""
        with patch("app.tools.syllabus_generator.tools.ParserFactory.create_parsers", 
                side_effect=Exception("Test error")):
            with pytest.raises(CompilePipelineError):
                pipeline.compile()

# Test Course Content Resume
class TestCourseContentResume:
    """Test suite for course content resume functionality."""
    
    def test_resume_course_content(self):
        """Test the resume_course_content function."""
        course_content = [
            {"unit_time": "weeks", "unit_time_value": 2, "topic": "Introduction"},
            {"unit_time": "weeks", "unit_time_value": 3, "topic": "Basic Concepts"},
            {"unit_time": "days", "unit_time_value": 5, "topic": "Review"}
        ]
        
        result = resume_course_content(course_content)
        assert isinstance(result, dict)
        assert "course_length" in result
        assert "course_topics" in result
        assert "5 weeks" in result["course_length"]
        assert "5 days" in result["course_length"]
