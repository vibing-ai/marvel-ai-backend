from app.features.ai_resistant_assignment.tools import validate_input_format, parse_ideas_from_response

def test_validate_input_format():
    assert validate_input_format("example.docx")
    assert validate_input_format("https://example.com")
    assert not validate_input_format("file.unsupported")

def test_parse_ideas_from_response():
    mock_response = """
    Update to make this Assignment AI-resistant (idea):
    Write a report on a personal experience related to the topic.
    Explanation: This requires individual reflection, which AI can't easily replicate.

    Update to make this Assignment AI-resistant (idea):
    Conduct an interview with a community member and summarize the insights.
    Explanation: AI can't access real-world conversations or personal interactions.
    """

    ideas = parse_ideas_from_response(mock_response, "8th")
    assert len(ideas) == 2
    assert ideas[0]["assignment_idea"].startswith("Write a report")
    assert ideas[1]["explanation"].startswith("AI can't access")
