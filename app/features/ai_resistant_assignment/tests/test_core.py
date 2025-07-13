from unittest.mock import patch, MagicMock
from app.features.ai_resistant_assignment.core import executor

@patch("app.features.ai_resistant_assignment.core.parse_ideas_from_response")
@patch("app.features.ai_resistant_assignment.core.get_chain")  
@patch("app.features.ai_resistant_assignment.core.extract_text_from_input")
@patch("app.features.ai_resistant_assignment.core.validate_input_format")
def test_executor_flow(mock_validate, mock_extract, mock_get_chain, mock_parse):
    mock_validate.return_value = True
    mock_extract.return_value = "Mock assignment text"

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "AI response text" 
    mock_get_chain.return_value = mock_chain

    mock_parse.return_value = [{"assignment_idea": "Idea A", "explanation": "because "}]

    result = executor("10th", "fake_path.docx")

    mock_validate.assert_called_once_with("fake_path.docx")
    mock_extract.assert_called_once()
    mock_chain.invoke.assert_called_once_with({
        "assignment_text": "Mock assignment text",
        "grade_level": "10th"
    })
    mock_parse.assert_called_once_with("AI response text", "10th")

    assert isinstance(result, list)
    assert result[0]["assignment_idea"] == "Idea A"
