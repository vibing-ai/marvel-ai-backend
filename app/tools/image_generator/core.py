from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from app.models import ImagePrompt, ImageResponse
from google.oauth2 import service_account
import logging
import os
from typing import Optional

# Configuration
PROJECT_ID = "eduimagegen"
LOCATION = "us-central1"
SERVICE_ACCOUNT_KEY_PATH = os.getenv(
    "SERVICE_ACCOUNT_KEY_PATH",
    "C:\\Users\melis\\OneDrive\\Masaüstü\\marvel-ai-backend\\marvel-ai-backend\\app\\eduimagegen-d664cc7b6af4.json"
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic safety filter keywords (expand as needed)
UNSAFE_KEYWORDS = {"inappropriate", "violent", "explicit"}

def enhance_prompt(prompt: str, subject: Optional[str] = None, grade_level: Optional[str] = None) -> str:
    """Enhance vague prompts with subject and grade-level context."""
    enhanced = prompt.strip()
    if subject and subject not in enhanced:
        enhanced += f", {subject}"
    if grade_level and grade_level not in enhanced:
        enhanced += f", {grade_level}"
    logger.info(f"Enhanced prompt: '{prompt}' -> '{enhanced}'")
    return enhanced

def is_prompt_safe(prompt: str) -> bool:
    """Check if the prompt contains unsafe content."""
    prompt_lower = prompt.lower()
    if any(keyword in prompt_lower for keyword in UNSAFE_KEYWORDS):
        logger.warning(f"Blocked unsafe prompt: '{prompt}'")
        return False
    return True

def generate_educational_image(prompt_data: ImagePrompt) -> ImageResponse:
    """Generate an educational image description from a text prompt using Gemini 2.0 Pro."""
    try:
        # Enhance the prompt with context
        enhanced_prompt = enhance_prompt(
            prompt_data.prompt,
            subject=prompt_data.subject,
            grade_level=prompt_data.grade_level
        )

        # Safety check
        if not is_prompt_safe(enhanced_prompt):
            return ImageResponse(
                image_url="",
                prompt_used=enhanced_prompt,
                success=False,
                error_message="Prompt rejected due to unsafe content"
            )

        # Initialize credentials and Vertex AI
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_PATH)
        logger.info(f"Using credentials for project: {creds.project_id}")  # Should log "eduimagegen"
        aiplatform.init(credentials=creds, location=LOCATION)  # Explicit region

        # Load Gemini model
        model = GenerativeModel("gemini-2.0-pro")
        logger.info(f"Generating content for prompt: '{enhanced_prompt}'")

        # Generate content (text output for now)
        response = model.generate_content(enhanced_prompt)
        text_output = response.text

        # Placeholder for image URL
        return ImageResponse(
            image_url="",  # To be updated with image generation
            prompt_used=enhanced_prompt,
            success=True,
            error_message=f"Text output: {text_output}"
        )

    except Exception as e:
        logger.error(f"Error in generate_educational_image: {str(e)}")
        return ImageResponse(
            image_url="",
            prompt_used=prompt_data.prompt,
            success=False,
            error_message=f"Image generation failed: {str(e)}"
        )