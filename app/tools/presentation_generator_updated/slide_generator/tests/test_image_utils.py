from app.tools.presentation_generator_updated.slide_generator.image_utils import build_prompt, get_image_size, needs_image

def test_build_prompt():
    prompt = build_prompt(
        title="Quantum Entanglement",
        content=["Linked particles", "Instant state change", "Non-locality"],
        layout="titleBullets"
    )
    assert "Quantum Entanglement" in prompt
    assert "Linked particles" in prompt
    assert "infographic" in prompt

def test_needs_image_true():
    assert needs_image("Quantum Applications", ["Machine learning", "Simulation", "Optimization"], "twoColumn") is True

def test_needs_image_false_on_title_slide():
    assert needs_image("Introduction Slide", "", "titleBody") is False

def test_get_image_size_default():
    assert get_image_size("unknownLayout") == (1024, 768)
