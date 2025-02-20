import pytest
from unittest.mock import patch, MagicMock, Mock
import os
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from app.tools.multiple_choice_quiz_generator.tools import (
    transform_json_dict, read_text_file, QuizBuilderConfig, QuizBuilder, RetrieverFactory, Document
)

class QuizBuilderFactory:
    """
    Factory class to create QuizBuilder instances with default or custom configurations.
    """
    @staticmethod
    def create_quiz_builder(topic = "Science",
                            n_questions = 5,
                            lang = "en",
                            grade_level = "High School",
                            quiz_description = "Sample quiz",
                            config = QuizBuilderConfig()):
        
        user_input = {
                        "topic": topic,
                        "n_questions": n_questions,
                        "grade_level": grade_level,
                        "quiz_description": quiz_description,
                        "lang": lang,
                        "config": config
        }
        return QuizBuilder(**user_input)

@pytest.fixture
def config():
    return QuizBuilderConfig()

@pytest.fixture
def quiz_builder(config):
    return QuizBuilderFactory.create_quiz_builder(config=config)

@pytest.fixture
def factory(config):
    return RetrieverFactory(config)

def test_transform_json_dict():
    input_data = {
        "questions_list": [
            {
                "question": "What is the capital of France?",
                "choices": [
                    {"key": "A", "value": "Berlin"},
                    {"key": "B", "value": "Madrid"},
                    {"key": "C", "value": "Paris"},
                    {"key": "D", "value": "Rome"},
                ],
                "answer": "C",
                "explanation": "Paris is the capital of France."
            }
        ]
    }
    expected_output = [
        {
            "question": "What is the capital of France?",
            "choices": {"A": "Berlin", "B": "Madrid", "C": "Paris", "D": "Rome"},
            "answer": "C",
            "explanation": "Paris is the capital of France."
        }
    ]
    assert transform_json_dict(input_data) == expected_output

def test_read_text_file():
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "sample text"
        
        # Adjust the expected path to match the absolute path construction in read_text_file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        expected_path = os.path.join(script_dir, "dummy_path.txt")
        
        result = read_text_file(expected_path)
        assert result == "sample text"
        mock_open.assert_called_once_with(expected_path, 'r')

def test_quiz_builder_config_initialization(config):
    assert config.max_questions == 10
    assert config.min_questions == 1
    assert config.max_attempts == 2
    assert config.prompt_template_path == "prompt/multiple_choice_quiz_generator_prompt.txt"
    assert config.multi_query_prompt_path == "prompt/multi_query_prompt.txt"
    assert config.verbose == False
    assert config.score_threshold == 0.4

def test_quiz_builder_initialization(config, quiz_builder):
    assert quiz_builder.topic == "Science"
    assert quiz_builder.lang == 'en'
    assert quiz_builder.grade_level == "High School"
    assert quiz_builder.n_questions == 5
    assert quiz_builder.quiz_description == "Sample quiz"
    assert quiz_builder.config == config
    assert quiz_builder.verbose == False

def test_quiz_builder_custom_initialization(config):
    user_input = {
        "topic": "Chemistry",
        "n_questions": 10,
        "grade_level": "High School",
        "quiz_description": "Create a quiz on Chemistry",
        "lang": "pt",
        "config": config
    }
    quiz_builder = QuizBuilder(**user_input)
    for key, value in user_input.items():
        assert getattr(quiz_builder, key) == value, \
        f"Expected {key} to be {value}, but got {getattr(quiz_builder, key)}"

def test_compile(quiz_builder):
    documents = [Document(page_content="Sample content")]
    chain = quiz_builder.compile(documents)
    assert chain is not None

def test_create_questions(quiz_builder):
    documents = [Document(page_content="Sample content")]
    with patch.object(quiz_builder, 'compile', return_value=MagicMock()) as mock_compile:
        with patch.object(quiz_builder, 'run_chain', return_value=[{"question": "Sample question", "choices": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}, "answer": "A", "explanation": "Sample explanation"}]):
            questions = quiz_builder.create_questions(documents)
            assert len(questions) == 1
            assert questions[0]["question"] == "Sample question"

def test_validate_response(quiz_builder):
    valid_response = {
        "question": "Sample question",
        "choices": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
        "answer": "A",
        "explanation": "Sample explanation"
    }
    assert quiz_builder.validate_response(valid_response) == True

    invalid_response = {
        "question": "Sample question",
        "choices": {"A": "Option A", "B": "Option B", "C": "Option C"},
        "answer": "A",
        "explanation": "Sample explanation"
    }
    assert quiz_builder.validate_response(invalid_response) == False

def test_format_choices(quiz_builder):
    choices = {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}
    formatted_choices = quiz_builder.format_choices(choices)
    assert formatted_choices == choices

def test_cleanup(quiz_builder):
    with patch.object(quiz_builder.vectorstore_manager, 'cleanup') as mock_cleanup:
        with patch.object(quiz_builder.retriever_factory, 'cleanup') as mock_retriever_cleanup:
            quiz_builder.cleanup()
            mock_cleanup.assert_called_once()
            mock_retriever_cleanup.assert_called_once()
            
def test_run_chain_max_attempts():
    config = QuizBuilderConfig(max_attempts=3)
    quiz_builder = QuizBuilderFactory.create_quiz_builder(config=config)
    chain_mock = MagicMock()
  
    with patch.object(chain_mock, 'invoke', side_effect=Exception("Test Exception")):
        with pytest.raises(Exception, match="Test Exception"):
            quiz_builder.run_chain(chain_mock, {} )
        assert chain_mock.invoke.call_count == config.max_attempts

def test_quiz_builder_config_default_initialization(config):
    assert isinstance(config.model, GoogleGenerativeAI)
    assert isinstance(config.embedding_model, GoogleGenerativeAIEmbeddings)
    assert config.vectorstore_class == Chroma
    assert config.max_questions == 10
    assert config.min_questions == 1
    assert config.max_attempts == 2
    assert config.prompt_template_path == "prompt/multiple_choice_quiz_generator_prompt.txt"
    assert config.multi_query_prompt_path == "prompt/multi_query_prompt.txt"
    assert config.verbose == False
    assert config.score_threshold == 0.4
    assert config.prompt_template is not None
    assert config.multi_query_prompt_template is not None
    assert isinstance(config.parser, JsonOutputParser)

def test_quiz_builder_config_custom_initialization():
    custom_model = MagicMock()
    custom_embedding_model = MagicMock()
    custom_vectorstore_class = MagicMock()
    custom_parser = MagicMock()

    config = QuizBuilderConfig(
        model=custom_model,
        embedding_model=custom_embedding_model,
        vectorstore_class=custom_vectorstore_class,
        max_questions=20,
        min_questions=5,
        max_attempts=3,
        parser=custom_parser,
        verbose=True,
        score_threshold=0.5
    )

    assert config.model == custom_model
    assert config.embedding_model == custom_embedding_model
    assert config.vectorstore_class == custom_vectorstore_class
    assert config.max_questions == 20
    assert config.min_questions == 5
    assert config.max_attempts == 3
    assert config.verbose == True
    assert config.score_threshold == 0.5
    assert config.prompt_template is not None
    assert config.multi_query_prompt_template is not None
    assert config.parser == custom_parser

def test_create_multiquery_prompt(factory):
    # Test prompt creation
    prompt = factory.create_multiquery_prompt(num_questions=5)
    assert isinstance(prompt, PromptTemplate)
    assert "num_questions" in prompt.partial_variables

def test_create_base_retriever(factory):
    # Mock vectorstore
    mock_vectorstore = Mock()
    mock_vectorstore.as_retriever.return_value = Mock()
    
    retriever = factory.create_base_retriever(
        vectorstore=mock_vectorstore,
        retriever_k=3,
        score_threshold=0.5
    )
    
    # Verify the retriever was created with correct params
    mock_vectorstore.as_retriever.assert_called_once_with(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5}
    )

def test_get_optional_instructions(quiz_builder):

    # Test cases
    test_cases = [
        {
            "input_name": "quiz_description",
            "input_value": "This is a test quiz",
            "expected": "- Assessment Description: This is a test quiz"
        },
        {
            "input_name": "non_existent",
            "input_value": "Some value",
            "expected": ""
        },
        {
            "input_name": "quiz_description",
            "input_value": "description",
            "expected": "- Assessment Description: description"
        }
    ]
    
    # Act & Assert
    for case in test_cases:
        result = quiz_builder.get_optional_instructions(
            case["input_name"],
            case["input_value"]
        )
        assert result == case["expected"], \
            f"Failed for input_name={case['input_name']}, input_value={case['input_value']}"