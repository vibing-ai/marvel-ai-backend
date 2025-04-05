import pytest
from unittest.mock import patch, MagicMock
from app.tools.presentation_generator_updated.slide_generator.tools import SlideGenerator, SlideGeneratorInput

@pytest.fixture
def mock_image_urls():
    return {
        'Introduction to Linear Algebra: What is it and why does it matter?': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/Introduction%20to%20Linear%20Algebra%20What%20is%20it%20and%20why%20does%20it%20matter_20250328_110744.png',
        'What is Linear Algebra?': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/What%20is%20Linear%20Algebra_20250328_110746.png',
        'Why is Linear Algebra Important?': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/Why%20is%20Linear%20Algebra%20Important_20250328_110744.png',
        'Linear Algebra in Action: Real-World Examples': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/Linear%20Algebra%20in%20Action%20Real-World%20Examples_20250328_110746.png',
        'Linear Equations vs. Linear Transformations': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/Linear%20Equations%20vs%20Linear%20Transformations_20250328_110748.png'
    }

@pytest.fixture
def mock_response():
    return {
        "slides": [
            {
                "title": "Introduction to Linear Algebra: What is it and why does it matter?",
                "template": "titleAndBody",
                "content": ["Understanding the fundamentals", "Key concepts and applications"]
            },
            {
                "title": "What is Linear Algebra?",
                "template": "twoColumn",
                "content": {"left": "Basic definitions", "right": "Core components"}
            },
            {
                "title": "Why is Linear Algebra Important?",
                "template": "titleAndBullets",
                "content": ["Applications in data science", "Role in machine learning"]
            }
        ]
    }

@pytest.fixture
def mock_args():
    return MagicMock(
        topic="Linear Algebra",
        instructional_level="university",
        slides_titles=[
            "Introduction to Linear Algebra: What is it and why does it matter?",
            "What is Linear Algebra?",
            "Why is Linear Algebra Important?"
        ],
        lang="en"
    )

@pytest.fixture
def slide_generator(mock_args):
    with patch("app.tools.presentation_generator_updated.slide_generator.tools.GoogleGenerativeAI"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.GoogleGenerativeAIEmbeddings"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.Chroma"):
        return SlideGenerator(args=mock_args)

def test_generate_slides_with_images(slide_generator, mock_response, mock_image_urls):
    # Mock the compile_context chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response
    slide_generator.compile_context = MagicMock(return_value=mock_chain)
    
    # Mock the image executor
    with patch("app.tools.presentation_generator_updated.slide_generator.tools.image_executor", return_value=mock_image_urls):
        result = slide_generator.generate_slides()
        
        assert isinstance(result, dict)
        assert "slides" in result
        assert len(result["slides"]) == 3
        
        # Verify slide titles match
        slide_titles = [slide["title"] for slide in result["slides"]]
        expected_titles = [
            "Introduction to Linear Algebra: What is it and why does it matter?",
            "What is Linear Algebra?",
            "Why is Linear Algebra Important?"
        ]
        assert slide_titles == expected_titles

def test_generate_slides_validation(slide_generator, mock_response, mock_image_urls):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response
    slide_generator.compile_context = MagicMock(return_value=mock_chain)
    
    with patch("app.tools.presentation_generator_updated.slide_generator.tools.image_executor", return_value=mock_image_urls):
        result = slide_generator.generate_slides()
        
        # Test validation results
        validation = slide_generator.validate_slides_content(result, "Linear Algebra")
        assert validation["valid"] is True
        assert validation["topic_coverage"] > 70
        assert validation["template_requirements_met"] is True

def test_generate_slides_image_executor_error(slide_generator, mock_response):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response
    slide_generator.compile_context = MagicMock(return_value=mock_chain)
    
    # Mock image_executor to raise an exception
    with patch("app.tools.presentation_generator_updated.slide_generator.tools.image_executor", 
              side_effect=Exception("Image generation failed")):
        with pytest.raises(Exception, match="Image generation failed"):
            slide_generator.generate_slides()

def test_generate_slides_empty_response(slide_generator):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = {"slides": []}
    slide_generator.compile_context = MagicMock(return_value=mock_chain)
    
    with patch("app.tools.presentation_generator_updated.slide_generator.tools.image_executor"):
        with pytest.raises(ValueError, match="No slides found in the response"):
            slide_generator.generate_slides()