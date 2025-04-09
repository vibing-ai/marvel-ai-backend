from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel
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
    "C:\\Users\\melis\\OneDrive\\Masaüstü\\marvel-ai-backend\\marvel-ai-backend\\app\\eduimagegen-d664cc7b6af4.json"
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
    """Generate an educational image using Imagen."""
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
        logger.info(f"Using credentials for project: {creds.project_id}")
        aiplatform.init(credentials=creds, location=LOCATION)

        # Load Imagen model
        model = ImageGenerationModel("imagen-3.0-fast")
        logger.info(f"Generating image for prompt: '{enhanced_prompt}'")

        # Generate image
        response = model.generate_images(prompt=enhanced_prompt, number_of_images=1)
        image_url = response.images[0]._image_data.decode()  # Adjust based on API response

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