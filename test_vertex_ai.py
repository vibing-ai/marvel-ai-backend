from app.tools.image_generator.core import generate_educational_image
from app.models import ImagePrompt, ImageResponse
import pytest

def test_generate_image_success():
    """Test that a valid prompt generates an image."""
    sample_prompt = ImagePrompt(prompt="plant cell", subject="biology", grade_level="middle school")
    response = generate_educational_image(sample_prompt)
    assert response.success, f"Failed: {response.error_message}"
    assert response.image_url != "", "Image URL should not be empty"

def test_generate_image_unsafe_prompt():
    """Test that an unsafe prompt is rejected."""
    unsafe_prompt = ImagePrompt(prompt="violent scene", subject="history", grade_level="high school")
    response = generate_educational_image(unsafe_prompt)
    assert not response.success
    assert "unsafe content" in response.error_message