from app.tools.presentation_generator_updated.slide_generator.image_utils import (
    build_prompt, needs_image, get_image_size
)

def test_prompt_with_style_and_tone():
    prompt = build_prompt(
        "Ecosystem Balance",
        ["Producers", "Consumers", "Decomposers"],
        layout="titleBullets",
        style="vibrant, infographic",
        tone="environmental science"
    )
    assert "vibrant, infographic" in prompt
    assert "environmental science" in prompt
    assert "Ecosystem Balance" in prompt

def test_needs_image_for_detailed_slide():
    assert needs_image("Applications of AI", ["Vision", "NLP", "Robotics"], "titleBullets") is True

def test_does_not_need_image_for_title_slide():
    assert needs_image("Title Slide", "Welcome", "sectionHeader") is False

def test_get_image_size_defaults():
    assert get_image_size("unknownLayout") == (1024, 768)
