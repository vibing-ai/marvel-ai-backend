import json
import os
import uuid
from typing import Any, Dict, List
import pytest
from unittest.mock import patch
from langsmith import Client
from app.utils.document_loaders import get_docs
from app.tools.multiple_choice_quiz_generator.tools import QuizBuilder, QuizBuilderConfig, transform_json_dict
from app.tools.multiple_choice_quiz_generator.tests.quiz_evaluator import QuizEvaluator
from pydantic import ValidationError

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TESTS_DIR, "test_data")

# Define the metrics values
METRICS_VALUES = {
    "content_alignment": 4,
    "uniqueness": 4,
    "coverage": 4,
    "overall_score": 4,
    "pct_docs_retrieved": 85
}

@pytest.fixture
def verbose():
    return False

@pytest.fixture
def ls_client():
    return Client()

@pytest.fixture
def quiz_builder_config():
    return QuizBuilderConfig()

@pytest.fixture
def evaluator():
    return QuizEvaluator()

@pytest.fixture
def ls_client():
    return Client()

def use_cases():
    """
        Load the test cases from the JSON file.
    """
    # Path to the JSON file
    test_cases_file = os.path.join(TESTS_DIR, "test_data/test_cases.json")
    
    try:
        # Load and parse the JSON file
        with open(test_cases_file, "r") as file:
            test_cases = json.load(file)
    
        return test_cases[:1]
    except Exception as e:
        return []

@pytest.mark.parametrize("input", use_cases())
def test_end_to_end_flow(input, verbose, evaluator, ls_client):
    """
    Test the end-to-end flow of the quiz generation process.
    """
    run_id = uuid.uuid4()
    docs = mock_remote_doc_loading(input["file_name"], input["file_type"], input["lang"])

    try:
        quiz_builder = QuizBuilder(
            topic=input["topic"],
            quiz_description=f"Test quiz about {input['topic']}", 
            lang=input["lang"], 
            verbose=verbose
        )

        chain = quiz_builder.compile(docs, input["n_questions"])
        
        # Fix the chain invocation
        response = chain.invoke(
            f"Topic: {quiz_builder.topic}, Lang: {quiz_builder.lang}",  # This is the input
            config={"callbacks": None, "run_id": run_id}  # This is the config
        )

        questions_list = parse_response_to_dict(response)

        if questions_list and len(questions_list) > 0:
            assert len(questions_list) == input["n_questions"], "Number of question generated is invalid"
            number_retrieved_docs = quiz_builder.retriever_factory.number_retrieved_docs

            valid_questions = validate_response(quiz_builder, questions_list)
            assert valid_questions == input["n_questions"], "Invalid response format"
        
            create_metrics(docs, questions_list, run_id, evaluator, number_retrieved_docs, ls_client)
    finally:
        quiz_builder.cleanup()

def validate_response(quiz_builder, question_list):
    """
        Validate the response format of the quiz questions.
    """
    valid_questions = 0
    for question in question_list:
        # Directly check if the response format is valid
        if quiz_builder.validate_response(question):
            valid_questions += 1
    return valid_questions

def parse_response_to_dict(json_response):
    """
    Parse the JSON response to a dictionary.
    """
    if json_response is None:
        raise AssertionError("Chain returned None response")
        
    try:
        return transform_json_dict(json_response)
    except ValidationError as e:
        raise AssertionError(f"Output json invalid: {str(e)}")
    except Exception as e:
        raise AssertionError(f"Failed to parse response: {str(e)}")

def read_file_content(file_url, file_type):
    """
        Read the content of a file based on its type.
    """
    open_mode = "r" if file_type in ("csv", "txt") else "rb"
   
    try:
        with open(file_url, open_mode) as file:
            file_content = file.read()  
        return file_content
    except Exception as e:
        assert False, e

def mock_remote_doc_loading(file_name, file_type, lang):
    """
        Mock the remote document loading process.
    """

    # Use the path of the local file for the URL
    file_url = os.path.join(TEST_DATA_DIR, file_name)

    file_content = read_file_content(file_url, file_type)

    with patch("app.utils.document_loaders.requests.head") as mock_head, \
         patch("app.utils.document_loaders.requests.get") as mock_content:
        
        # Simulate that the Content-Type header is valid for testing
        mock_head.return_value.headers = {"Content-Type": "text/plain"}
        mock_content.return_value.content = file_content
        mock_content.return_value.status = 200

        # Call the function to load the file content (no mocks for file loading)
        docs = get_docs(file_url, file_type, lang)
        return docs

def create_metrics(docs, questions_list, run_id, evaluator, number_retrieved_docs, ls_client):
    """
        Create metrics for the quiz evaluation.
    """
    try:
        metrics = evaluator.evaluate_quiz(docs, questions_list, run_id)
    
        metrics["pct_docs_retrieved"] = round((number_retrieved_docs / len(docs)) * 100, 0)

        assert metrics["content_alignment"]["score"] >= METRICS_VALUES["content_alignment"] , "Content alignment score is less than 4"
        assert metrics["uniqueness"]["score"] >= METRICS_VALUES["uniqueness"], "Uniqueness score is less than 4"
        assert metrics["coverage"]["score"] >= METRICS_VALUES["coverage"], "Coverage score is less than 4"
        assert metrics["overall_score"] >= METRICS_VALUES["overall_score"],   "Overall score is less than 4"
        assert metrics["pct_docs_retrieved"] >= METRICS_VALUES["pct_docs_retrieved"], "Retrieval percent less than 90%"

        ls_client.create_feedback(run_id, 
                                  key="content_alignment", 
                                  value=metrics["content_alignment"]["score"],
                                  comment=metrics["content_alignment"]["reasoning"]) 
        ls_client.create_feedback(run_id, 
                                  key="uniqueness", 
                                  value=metrics["uniqueness"]["score"],
                                  comment=metrics["uniqueness"]["reasoning"])
        ls_client.create_feedback(run_id, 
                                  key="coverage", 
                                  value=metrics["coverage"]["score"],
                                  comment=metrics["coverage"]["reasoning"])
        ls_client.create_feedback(run_id, 
                                  key="overall_score", 
                                  value=metrics["overall_score"],
                                  comment=metrics["overall_feedback"])
        ls_client.create_feedback(run_id, 
                                  key="pct_docs_retrieved", 
                                  value=metrics["pct_docs_retrieved"],
                                  comment="Percentage of documents retrieved")

    except Exception as e:
        assert False, e