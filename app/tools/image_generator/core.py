from google.cloud import aiplatform
from google.oauth2 import service_account
import logging
import os
import requests
from app.models import ImagePrompt, ImageResponse
from typing import Optional
from google.auth.transport.requests import Request

# Configuration
PROJECT_ID = "eduimagegen"
LOCATION = "us-central1"
MODEL_ID = "imagen-3.0-generate-002"  # Switch to Imagen 3 model
SERVICE_ACCOUNT_KEY_PATH = os.getenv(
    "SERVICE_ACCOUNT_KEY_PATH",
    "C:\\Users\\melis\\OneDrive\\Masaüstü\\marvel-ai-backend\\marvel-ai-backend\\app\\eduimagegen-d664cc7b6af4.json"
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UNSAFE_KEYWORDS = {"inappropriate", "violent", "explicit"}

def enhance_prompt(prompt: str, subject: Optional[str] = None, grade_level: Optional[str] = None) -> str:
    enhanced = prompt.strip()
    if subject and subject not in enhanced:
        enhanced += f", {subject}"
    if grade_level and grade_level not in enhanced:
        enhanced += f", {grade_level}"
    logger.info(f"Enhanced prompt: '{prompt}' -> '{enhanced}'")
    return enhanced

def is_prompt_safe(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    if any(keyword in prompt_lower for keyword in UNSAFE_KEYWORDS):
        logger.warning(f"Blocked unsafe prompt: '{prompt}'")
        return False
    return True

def generate_educational_image(prompt_data: ImagePrompt) -> ImageResponse:
    try:
        enhanced_prompt = enhance_prompt(
            prompt_data.prompt,
            subject=prompt_data.subject,
            grade_level=prompt_data.grade_level
        )

        if not is_prompt_safe(enhanced_prompt):
            return ImageResponse(
                image_url="",
                prompt_used=enhanced_prompt,
                success=False,
                error_message="Prompt rejected due to unsafe content"
            )

        # Initialize credentials with proper scope
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY_PATH,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        # Refresh token explicitly
        if not creds.valid:
            creds.refresh(Request())
        token = creds.token

        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:predict"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "instances": [{"prompt": enhanced_prompt}],
            "parameters": {
                "sampleCount": 1,
                "enhancePrompt": True  # Enable prompt enhancement (default for Imagen 3)
            }
        }

        logger.info(f"Generating image for prompt: '{enhanced_prompt}'")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        image_data = result["predictions"][0]["bytesBase64Encoded"]
        image_url = f"data:image/png;base64,{image_data}"

        return ImageResponse(
            image_url=image_url,
            prompt_used=enhanced_prompt,
            success=True,
            error_message=""
        )
    except Exception as e:
        logger.error(f"Error in generate_educational_image: {str(e)}")
        return ImageResponse(
            image_url="",
            prompt_used=prompt_data.prompt,
            success=False,
            error_message=f"Image generation failed: {str(e)}"
        )