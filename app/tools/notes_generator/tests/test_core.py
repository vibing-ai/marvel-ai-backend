import pytest
from typing import Dict
from app.tools.notes_generator.core import executor
from app.api.error_utilities import ToolExecutorError


def test_executor_valid_text_input() -> None:
    """
    Tests the note generation with valid text input.
    Ensures that the generated output contains summary, bullet points, and a table.
    """

    # Arrange: Define the input data
    input_text: str = "Machine learning is a branch of AI."
    focus: str = "Summary"
    lang: str = "en"

    # Act: Execute the function
    result: Dict[str, str] = executor(
        input_text=input_text, focus=focus, file_url=None, file_type=None, lang=lang
    )

    # Assert: Validate the output structure
    assert isinstance(result, dict)
    assert "summary" in result
    assert "bullet_points" in result
    assert "table" in result


def test_executor_empty_text_input() -> None:
    """
    Tests if an error is raised when passing an empty text input.
    The function should raise a ValueError.
    """

    # Arrange: Define an empty text input
    input_text: str = ""
    focus: str = "Summary"
    lang: str = "en"

    # Act & Assert: Ensure the function raises ValueError
    with pytest.raises(ValueError):
        executor(input_text=input_text, focus=focus, file_url=None, file_type=None, lang=lang)


def test_executor_invalid_file_type() -> None:
    """
    Tests if an error is raised when passing an unsupported file type.
    The function should raise a ToolExecutorError.
    """

    # Arrange: Define an unsupported file type
    input_text: str = "Test"
    focus: str = "Summary"
    file_url: str = "invalid.xyz"
    file_type: str = "xyz"
    lang: str = "en"

    # Act & Assert: Ensure the function raises ToolExecutorError
    with pytest.raises(ToolExecutorError):
        executor(input_text=input_text, focus=focus, file_url=file_url, file_type=file_type, lang=lang)
