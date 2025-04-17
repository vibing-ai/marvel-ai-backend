import pytest
from unittest.mock import patch, MagicMock
import os
import json
from app.tools.image_generator.tools import ImageGenerator, ImageGeneratorArgs, ImageGenerationResult

def test_image_generator_initialization():
    """Test that the ImageGenerator initializes correctly."""
    args = ImageGeneratorArgs(
        prompt="A diagram of the solar system",
        subject="astronomy",
        grade_level="middle school",
        lang="en"
    )
    
    generator = ImageGenerator(args=args, verbose=True)
    
    assert generator.args == args
    assert generator.verbose == True
    assert generator.model is not None

@patch('app.tools.image_generator.tools.GoogleGenerativeAI')
def test_enhance_prompt_with_educational_context_provided(mock_model):
    """Test enhancing prompt with provided educational context."""
    args = ImageGeneratorArgs(
        prompt="A diagram of the solar system",
        subject="astronomy",
        grade_level="middle school",
        lang="en"
    )
    
    generator = ImageGenerator(args=args)
    
    result = generator.enhance_prompt_with_educational_context(
        prompt="A diagram of the solar system",
        subject="astronomy",
        grade_level="middle school"
    )
    
    assert result["enhanced_prompt"] == "A diagram of the solar system, educational context: astronomy for middle school level"
    assert result["educational_context"] == "astronomy for middle school level"

@patch('app.tools.image_generator.tools.GoogleGenerativeAI')
def test_check_prompt_safety_unsafe(mock_model):
    """Test that unsafe prompts are detected."""
    mock_instance = mock_model.return_value
    mock_instance.invoke.return_value = "UNSAFE"
    
    args = ImageGeneratorArgs(
        prompt="A diagram of the solar system",
        lang="en"
    )
    
    generator = ImageGenerator(args=args)
    
    # Test with an unsafe keyword
    result = generator.check_prompt_safety("A violent explosion")
    assert result == False

@patch('app.tools.image_generator.tools.GoogleGenerativeAI')
def test_generate_image(mock_model):
    """Test image generation."""
    mock_instance = mock_model.return_value
    mock_instance.invoke.return_value = "Generated image response"
    
    args = ImageGeneratorArgs(
        prompt="A diagram of the solar system",
        subject="astronomy",
        grade_level="middle school",
        lang="en"
    )
    
    generator = ImageGenerator(args=args)
    
    result = generator.generate_image("A diagram of the solar system, educational context: astronomy for middle school level")
    
    assert "image_b64" in result
    assert result["prompt_used"] == "A diagram of the solar system, educational context: astronomy for middle school level"

@patch('app.tools.image_generator.tools.ImageGenerator.check_prompt_safety')
@patch('app.tools.image_generator.tools.ImageGenerator.enhance_prompt_with_educational_context')
@patch('app.tools.image_generator.tools.ImageGenerator.generate_image')
def test_generate_educational_image(mock_generate, mock_enhance, mock_safety):
    """Test the full educational image generation pipeline."""
    mock_safety.return_value = True
    mock_enhance.return_value = {
        "enhanced_prompt": "A diagram of the solar system, educational context: astronomy for middle school level",
        "educational_context": "astronomy for middle school level"
    }
    mock_generate.return_value = {
        "image_b64": "base64_encoded_image_data",
        "prompt_used": "A diagram of the solar system, educational context: astronomy for middle school level"
    }
    
    args = ImageGeneratorArgs(
        prompt="A diagram of the solar system",
        subject="astronomy",
        grade_level="middle school",
        lang="en"
    )
    
    generator = ImageGenerator(args=args)
    
    result = generator.generate_educational_image()
    
    assert isinstance(result, ImageGenerationResult)
    assert result.image_b64 == "base64_encoded_image_data"
    assert result.prompt_used == "A diagram of the solar system, educational context: astronomy for middle school level"
    assert result.educational_context == "astronomy for middle school level"
    assert result.safety_applied == True
