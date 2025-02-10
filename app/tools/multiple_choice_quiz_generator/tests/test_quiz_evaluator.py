import json
import os
import uuid
from typing import Any, Dict, List
import pytest
from unittest.mock import patch
from langsmith import Client, traceable
from app.utils.document_loaders import get_docs
from app.tools.multiple_choice_quiz_generator.tools import QuizBuilder, QuizBuilderConfig, transform_json_dict
from app.tools.multiple_choice_quiz_generator.tests.quiz_evaluator import QuizEvaluator
from pydantic import ValidationError

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

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

def use_cases():
    # Path to the JSON file
    test_cases_file = os.path.join(TESTS_DIR, "test_data/test_cases.json")
    
    # Load and parse the JSON file
    with open(test_cases_file, "r") as file:
        test_cases = json.load(file)
    
    return test_cases[:]


@pytest.mark.parametrize("input", use_cases())
def test_end_to_end_flow(input, verbose, evaluator):
    run_id = uuid.uuid4()
    docs = get_docs_from_local_file(input["file_name"], input["file_type"], input["lang"])

    try:
        quiz_builder = QuizBuilder(input["topic"], input["lang"], verbose=verbose)

        chain = quiz_builder.compile(docs, input["n_questions"])
        # response = chain.invoke(f"Topic: {quiz_builder.topic}, Lang: {quiz_builder.lang}")
        response = chain.invoke({"input": f"Topic: {quiz_builder.topic}, Lang: {quiz_builder.lang}"}, {"run_id": run_id})

        questions_list = to_dict(response)

        if questions_list and len(questions_list) > 0:
            assert len(questions_list) == input["n_questions"], "Number of question generated is invalid"
            number_retrieved_docs = quiz_builder.retriever_factory.number_retrieved_docs

            valid_questions = validate_response(quiz_builder, questions_list)
            assert valid_questions == input["n_questions"], "Invalid response format"
        
            create_metrics(docs, questions_list, run_id, evaluator, number_retrieved_docs)
    finally:
        quiz_builder.cleanup()
        quiz_builder = None

def validate_response(quiz_builder, question_list):
    valid_questions = 0
    for question in question_list:
        # Directly check if the response format is valid
        if quiz_builder.validate_response(question):
            valid_questions += 1
    return valid_questions

def to_dict(json):
    try:
        return transform_json_dict(json)
    except ValidationError as e:
        assert False, "Output json invalid"
        return []
    except Exception as e:
        assert False, e
        return []

def read_file_content(file_url, file_type):
    open_mode = "r" if file_type in ("csv", "txt") else "rb"
   
    with open(file_url, open_mode) as file:
        file_content = file.read()  
    return file_content

def get_docs_from_local_file(file_name, file_type, lang):
    # Use the path of the local file for the URL
    relative_path = "test_data"
    file_url = os.path.join(TESTS_DIR, relative_path, file_name)

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

def create_metrics(docs, questions_list, run_id, evaluator, number_retrieved_docs):
    try:
        metrics = evaluator.evaluate_quiz(docs, questions_list, run_id)
    
        metrics["pct_docs_retrieved"] = round((number_retrieved_docs / len(docs)) * 100, 0)

        assert metrics["content_alignment"]["score"] >= 4 , "Content alignment score is less than 4"
        assert metrics["uniqueness"]["score"] >= 4, "Uniqueness score is less than 4"
        assert metrics["coverage"]["score"] >= 4, "Coverage score is less than 4"
        assert metrics["overall_score"] >= 4,   "Overall score is less than 4"
        assert metrics["pct_docs_retrieved"] >= 90, "Retrieval percent less than 90%"

    except Exception as e:
        assert False, e