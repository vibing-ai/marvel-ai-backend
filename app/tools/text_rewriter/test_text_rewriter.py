import pytest
from core import executor
from tools import simplify_text

def test_executor_simplify_text():
    input_data = "Romeo and Juliet is a tragic play by William Shakespeare."
    instruction = "simplify"
    expected_output = "Romeo and Juliet is a sad play by William Shakespeare."
    assert executor(input_data, instruction) == expected_output

def test_simplify_text_function():
    original_text = "Romeo and Juliet is a tragic play."
    expected = "Romeo and Juliet is a sad play."
    assert simplify_text(original_text) == expected

