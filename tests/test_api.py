import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.services.logger import setup_logger

logger = setup_logger(__name__)

client = TestClient(app)

def test_generate_image_endpoint_success():
    logger.info("Testing successful image generation endpoint")
    response = client.post(
        "/api/generate-image",
        json={"prompt": "plant cell", "subject": "biology", "grade_level": "middle school"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["image_url"].startswith("data:image/png;base64,")

def test_generate_image_endpoint_unsafe():
    logger.info("Testing unsafe prompt rejection")
    response = client.post(
        "/api/generate-image",
        json={"prompt": "violent scene", "subject": "history", "grade_level": "high school"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "unsafe content" in data["detail"]

def test_generate_image_endpoint_missing_prompt():
    logger.info("Testing missing prompt validation")
    response = client.post(
        "/api/generate-image",
        json={"subject": "biology", "grade_level": "middle school"}
    )
    assert response.status_code == 422
    data = response.json()
    assert "prompt" in data["message"][0]