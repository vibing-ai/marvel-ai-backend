
import pytest
from app.tools.presentation_generator_updated.slide_generator.core import executor,SlideGeneratorInput
from unittest.mock import patch, MagicMock, Mock
from app.tools.presentation_generator_updated.slide_generator.tools import SlideGenerator, Slide,SlidePresentation
from app.tools.presentation_generator_updated.slide_generator.imagen import ImageGenerator
@pytest.fixture
def mock_slide_data():
        return  [
            {
                "title": "Introduction",
                "template": "titleAndBullets",
                "content": ["Key Point 1", "Key Point 2"],
                 "image_url": "https://example.com/image.png"
            },
            {
                "title": "Main Content",
                "template": "twoColumn",
                "content": {
                    "leftColumn": "Left column content",
                    "rightColumn": "Right column content"
                },
                "image_url": "https://example.com/image.png"
            }
        ]
    
@pytest.fixture
def mock_args():
    return SlideGeneratorInput(
        slides_titles=["Intro", "Details"],
        topic="Data Science",
        instructional_level="Intermediate",
        file_url="",
        file_type="",
        lang="en"
    )

@pytest.fixture
def base_input():
    return {
        "slides_titles": ["Introduction", "Main Content"],
        "topic": "Artificial Intelligence",
        "instructional_level": "intermediate",
        "file_url": "",
        "file_type": "",
        "lang": "en"
    }
@pytest.fixture
def mock_slide_generator():
    """Mock SlideGenerator instead of instantiating it."""
    with patch("app.tools.presentation_generator_updated.slide_generator.tools.GoogleGenerativeAI"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.GoogleGenerativeAIEmbeddings"), \
         patch("app.tools.presentation_generator_updated.slide_generator.tools.Chroma"),\
         patch("app.tools.presentation_generator_updated.slide_generator.tools.ImageGenerator") as mock_image_gen\
       :           
             
            # Set up firebase mock
            mock_firebase = MagicMock()
            mock_firebase.upload_image = MagicMock(return_value="https://example.com/image.png")
            # Patch the FirebaseManager singleton instance
            with patch("app.tools.presentation_generator_updated.slide_generator.firebase.FirebaseManager._instance", mock_firebase), \
                 patch("app.tools.presentation_generator_updated.slide_generator.firebase.FirebaseManager._initialized", True):
         
                slide_generator = SlideGenerator()
                # Set up image generator mock
                
                mock_image_generator = mock_image_gen.return_value
                mock_image_generator.generate_image = MagicMock()
                slide_generator.image_generator = mock_image_generator
                slide_generator.validate_slides_content = MagicMock()
                slide_generator.generate_slides = MagicMock()
                slide_generator.compile_context = MagicMock()
                slide_generator.compile_with_context = MagicMock()
            

            return slide_generator
    
#Test the executor function, we mock the generate_slides method.
def test_executor(mock_slide_data,mock_slide_generator,base_input):
    
    # Create a mock instance of SlideGenerator
    mock_slide_generator.generate_slides.return_value = mock_slide_data

    # Patch SlideGenerator to return the mock instance
    with patch("app.tools.presentation_generator_updated.slide_generator.core.SlideGenerator", return_value=mock_slide_generator):
        result = executor(**base_input,verbose=False)

    # Assertions
    assert result == mock_slide_data
    mock_slide_generator.generate_slides.assert_called_once() 
    assert len(result) == 2

   # Ensure the function was called once
def test_generate_slide_image(mock_args,mock_slide_generator):
    """Test image generation for a slide."""
    # Mock slide data
    slide_data = {
        "needs_image": True,
        "image_prompt": "Test prompt",
        "width": 1280,
        "height": 720,
        "template": "titleBody",
        "style": "modern",
        

    }
    mock_slide_generator.args = mock_args
    # Mock the image generator's response
    mock_slide_generator.image_generator.generate_image.return_value = MagicMock(_image_bytes=b"fake_image_data")
    
    
    # # Mock Firebase upload (assuming it exists)
    # mock_slide_generator.firebase.upload_image = MagicMock()
    # mock_slide_generator.firebase.upload_image.return_value = "https://example.com/image.png"
    
    # Create the image generation chain
    image_chain = mock_slide_generator.generate_slide_image(0, slide_data)
    
    # Execute the chain
    result = image_chain.invoke({})
    
    # Assertions
    assert result["slide_key"] == 0
    assert result["image_url"] == "https://example.com/image.png"
    mock_slide_generator.image_generator.generate_image.assert_called_once_with(0, slide_data)

#Test the executor function with missing required inputs.
def test_executor_missing_inputs():
    """Test the executor function with missing required inputs."""
    with pytest.raises(ValueError, match="Missing required inputs"):
        executor(
            slides_titles=[],
            topic="",
            instructional_level="",
            lang="en",
            file_type="",
            file_url=""
            
        )


#Test the validate_slides_content function.
def test_validate_slides_content(mock_slide_generator):
    # Define fake return value
    mock_slide_generator.validate_slides_content.return_value = {
        "topic_coverage": 80,
        "template_requirements_met": True,
        "garbage_coverage_percentage": 0,
        "valid": True
    }
    topic = "AI in Education"
    response = {"slides": [{"template": "twoColumn", "content": ["AI and learning"]}]}
    result = mock_slide_generator.validate_slides_content(response, topic)

    assert result["valid"] == True
    assert result["topic_coverage"] == 80
    
    

#Test the validate_slides_content function with garbage content.
def test_validate_slides_content_with_garbage(mock_slide_generator):
    topic = "Introduction"
    response = {
        "slides": [
            {
                "title": "Introduction",
                "template": "sectionHeader",  # Not "twoColumn"
                "content": ["Unrelated content", "* This should not be here"]
            }
        ]
    }
    # Mock the return value for an invalid response
    mock_slide_generator.validate_slides_content.return_value = {
        "topic_coverage": 20,
        "template_requirements_met": False,
        "garbage_coverage_percentage": 50,
        "valid": False
    }
    result = mock_slide_generator.validate_slides_content(response, topic)

    assert result["valid"] == False
    assert result["topic_coverage"] == 20
    assert result["template_requirements_met"] == False
    assert result["garbage_coverage_percentage"] == 50


#Test the validate_slides_content function with empty slides.
def test_validate_slides_content_empty_slides(mock_slide_generator):
    topic = "Introduction"
    response = {"slides": []}  # No slides

    # Mock the method to raise ValueError when slides are empty
    mock_slide_generator.validate_slides_content.side_effect = ValueError("No slides found in the response")

    with pytest.raises(ValueError, match="No slides found in the response"):
        mock_slide_generator.validate_slides_content(response, topic)

#Test the compile_with_context function.
def test_slide_generator_compile_context(mock_args,mock_slide_generator):
    """Test compilation of pipeline."""
    args = mock_args
    test_instance = mock_slide_generator
    test_instance.args = args    
    chain = test_instance.compile_context()    
    assert chain is not None

@patch("app.tools.presentation_generator_updated.slide_generator.imagen.ImageGenerationModel")
def test_imagen_generate_image(mock_imagen_model):
    """Test the ImageGenerator's generate_image method."""
    # Setup mock response with image data
    mock_image = MagicMock()
    mock_image._image_bytes = b"fake_image_data"
    mock_response = MagicMock()
    mock_response.images = [mock_image]
    
    # Setup mock model
    mock_model = MagicMock()
    mock_model.generate_images.return_value = mock_response
    mock_imagen_model.from_pretrained.return_value = mock_model

    # Create ImageGenerator instance and generate image
    image_generator = ImageGenerator()
    result = image_generator.generate_image(0, {
        "image_prompt": "A test image",
        "width": 1280,
        "height": 720,
        "template": "titleBody"
    })

    # Assertions
    assert result is not None
    assert result._image_bytes == b"fake_image_data"
    
    # Verify model was called correctly
    mock_model.generate_images.assert_called_once_with(
        prompt='Generate an image based on the following visual notes: A test image. The image should be 1280x720.',
        number_of_images=1,
        aspect_ratio="16:9",
        add_watermark=False
    )
#Test the Slide Pydantic model.
def test_slide_model():
    """Test the Slide Pydantic model."""
    slide = Slide(
        title="Introduction",
        template="titleAndBullets",
        content=["Key Point 1", "Key Point 2"],
        needs_image=True,
        image_prompt="Visual representation of key points",
        style="Modern"
    )
    
    assert slide.title == "Introduction"
    assert slide.template == "titleAndBullets"
    assert slide.content == ["Key Point 1", "Key Point 2"]
    
#Test the SlidePresentation Pydantic model.
def test_slide_presentation_model():
    """Test the SlidePresentation Pydantic model."""
    slides = [
        Slide(title="Intro", template="titleAndBody", content="Overview", needs_image=False, image_prompt="", style=""),
        Slide(title="Details", template="twoColumn", content={"left": "Content1", "right": "Content2"}, needs_image=True, image_prompt="Comparison", style="Minimalist")
    ]
    
    presentation = SlidePresentation(slides=slides)
    
    assert len(presentation.slides) == 2
    assert all(isinstance(slide, Slide) for slide in presentation.slides)
