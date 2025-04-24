import pytest
from unittest.mock import patch, MagicMock
from app.tools.image_generator.tools import (
    executor_image_generator,
    check_prompt_safety,
    read_prompt_file,
    map_language,
    save_to_cloud_storage,
    ImageGenerationError,
)

# --- Test Data --- #
VALID_INPUTS = {
    "base_prompt": "algebra equation",
    "grade_level": "Middle School",
    "subject": "Mathematics",
    "api_key": "fake_api_key",
    "project_id": "fake_project_id",
    "language": "English",
    "verbose": False,
}

# --- Fixtures --- #
@pytest.fixture
def mock_prompt_files(tmp_path):
    # Create prompt directory
    prompt_dir = tmp_path / "prompt"
    prompt_dir.mkdir()
    
    # Create test prompt files
    files = {
        "check_prompt.txt": "Check safety: {prompt} for {grade_level} {subject}",
        "enhancement.txt": "Enhance: {prompt} for {grade_level} {subject} in {language}",
        "prompt_positive.txt": "Make it educational and clear",
        "prompt_negative.txt": "Avoid inappropriate content",
    }
    
    for name, content in files.items():
        (prompt_dir / name).write_text(content)
    
    return str(prompt_dir.parent)  # Return parent directory instead of prompt dir

@pytest.fixture
def mock_gemini():
    return MagicMock(
        generate=lambda prompts: MagicMock(
            generations=[[MagicMock(text="SAFE")]]
        )
    )

@pytest.fixture
def mock_vertex_model():
    return MagicMock(
        generate_images=lambda **kwargs: MagicMock(
            images=[MagicMock(_image_bytes=b"fake_image_data")]
        )
    )

@pytest.fixture
def mock_firebase():
    return MagicMock(
        upload_image=lambda img, path: "https://storage.example.com/image.png"
    )

# --- Tests for read_prompt_file --- #
def test_read_prompt_file_success(mock_prompt_files, monkeypatch):
    monkeypatch.setattr("app.tools.image_generator.tools.os.path.dirname", lambda x: mock_prompt_files)
    content = read_prompt_file("check_prompt.txt")
    assert "Check safety" in content

def test_read_prompt_file_not_found(mock_prompt_files, monkeypatch):
    monkeypatch.setattr("app.tools.image_generator.tools.os.path.dirname", lambda x: mock_prompt_files)
    with pytest.raises(FileNotFoundError):
        read_prompt_file("nonexistent.txt")

# --- Tests for check_prompt_safety --- #
def test_check_prompt_safety_safe(mock_gemini):
    with patch("app.tools.image_generator.tools.GoogleGenerativeAI", return_value=mock_gemini):
        is_safe, message = check_prompt_safety(
            base_prompt="educational math concept",
            grade_level="Middle School",
            subject="Mathematics",
            api_key="fake_key"
        )
        assert is_safe
        assert "safe" in message.lower()

def test_check_prompt_safety_unsafe(mock_gemini):
    mock_gemini.generate = lambda prompts: MagicMock(
        generations=[[MagicMock(text="UNSAFE: inappropriate content")]]
    )
    with patch("app.tools.image_generator.tools.GoogleGenerativeAI", return_value=mock_gemini):
        is_safe, message = check_prompt_safety(
            base_prompt="inappropriate content",
            grade_level="Middle School",
            subject="Mathematics",
            api_key="fake_key"
        )
        assert not is_safe
        assert "unsafe" in message.lower()

# --- Tests for map_language --- #
@pytest.mark.parametrize("input_lang,expected", [
    (None, "en"),
    ("", "en"),
    ("English", "en"),
    ("Hindi", "hi"),
    ("Japanese", "ja"),
    ("Korean", "ko"),
    ("Unknown", "en"),
])
def test_map_language(input_lang, expected):
    assert map_language(input_lang) == expected

# --- Tests for executor_image_generator --- #
def test_executor_image_generator_success(mock_prompt_files, mock_gemini, mock_vertex_model, mock_firebase, monkeypatch):
    monkeypatch.setattr("app.tools.image_generator.tools.os.path.dirname", lambda x: mock_prompt_files)
    monkeypatch.setattr("app.tools.image_generator.tools.GoogleGenerativeAI", lambda **kwargs: mock_gemini)
    monkeypatch.setattr("vertexai.init", lambda **kwargs: None)
    monkeypatch.setattr("app.tools.image_generator.tools.ImageGenerationModel.from_pretrained", 
                        lambda model: mock_vertex_model)
    monkeypatch.setattr("app.tools.image_generator.tools.FirebaseManager", 
                        lambda: mock_firebase)

    result = executor_image_generator(**VALID_INPUTS)
    assert "image_url" in result
    assert isinstance(result["image_url"], str)

def test_executor_image_generator_unsafe_prompt(mock_prompt_files, mock_gemini, monkeypatch):
    mock_gemini.generate = lambda prompts: MagicMock(
        generations=[[MagicMock(text="UNSAFE: inappropriate content")]]
    )
    monkeypatch.setattr("app.tools.image_generator.tools.os.path.dirname", lambda x: mock_prompt_files)
    monkeypatch.setattr("app.tools.image_generator.tools.GoogleGenerativeAI", lambda **kwargs: mock_gemini)

    with pytest.raises(ValueError) as exc:
        executor_image_generator(**VALID_INPUTS)
    assert "Unsafe prompt" in str(exc.value)

def test_executor_image_generator_no_images(mock_prompt_files, mock_gemini, mock_vertex_model, monkeypatch):
    mock_vertex_model.generate_images = lambda **kwargs: MagicMock(images=[])
    monkeypatch.setattr("app.tools.image_generator.tools.os.path.dirname", lambda x: mock_prompt_files)
    monkeypatch.setattr("app.tools.image_generator.tools.GoogleGenerativeAI", lambda **kwargs: mock_gemini)
    monkeypatch.setattr("vertexai.init", lambda **kwargs: None)
    monkeypatch.setattr("app.tools.image_generator.tools.ImageGenerationModel.from_pretrained", 
                        lambda model: mock_vertex_model)

    with pytest.raises(ValueError) as exc:
        executor_image_generator(**VALID_INPUTS)
    assert "Model did not return any images" in str(exc.value)

# --- Tests for save_to_cloud_storage --- #
def test_save_to_cloud_storage_success(mock_firebase, monkeypatch):
    monkeypatch.setattr("app.tools.image_generator.tools.FirebaseManager", lambda: mock_firebase)
    image_url = save_to_cloud_storage(b"fake_image_data")
    assert isinstance(image_url, str)
    assert image_url.startswith("http")

def test_save_to_cloud_storage_failure(monkeypatch):
    mock_firebase = MagicMock()
    mock_firebase.upload_image.side_effect = Exception("Upload failed")
    monkeypatch.setattr("app.tools.image_generator.tools.FirebaseManager", lambda: mock_firebase)
    
    with pytest.raises(Exception):
        save_to_cloud_storage(b"fake_image_data")
