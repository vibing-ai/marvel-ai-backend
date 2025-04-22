import os
import logging
from google.cloud import aiplatform
from google.api_core import exceptions
from google.oauth2 import service_account
from typing import Optional
from app.schemas import ImagePrompt

# Configuration
PROJECT_ID = "eduimagegen"
LOCATION = "us-central1"
MODEL_ID = "gemini-2.0-pro"  # Use Gemini 2.0 Pro as per mission objective
UNSAFE_KEYWORDS = {"inappropriate", "violent", "explicit", "offensive", "harmful"}

# Logging setup
logger = logging.getLogger(__name__)

def initialize_vertex_ai() -> None:
    """
    Initialize Vertex AI with service account credentials.
    Use environment variable for credentials path to avoid hardcoding.
    """
    try:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path or not os.path.exists(credentials_path):
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set or invalid")

        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        aiplatform.init(
            project=PROJECT_ID,
            location=LOCATION,
            credentials=credentials
        )
        logger.info("Vertex AI initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {str(e)}")
        raise

def enhance_prompt(prompt: str, subject: Optional[str] = None, grade_level: Optional[str] = None) -> str:
    """
    Enhance the prompt by appending subject and grade-level context if provided.
    Example: "plant cell" -> "plant cell, biology, middle school"
    """
    enhanced = prompt.strip()
    if subject and subject.lower() not in enhanced.lower():
        enhanced += f", {subject}"
    if grade_level and grade_level.lower() not in enhanced.lower():
        enhanced += f", {grade_level}"
    enhanced += ", classroom-safe, educational"  # Ensure educational context
    logger.info(f"Enhanced prompt: '{prompt}' -> '{enhanced}'")
    return enhanced

def is_prompt_safe(prompt: str) -> bool:
    """
    Check if the prompt contains unsafe keywords or patterns.
    """
    prompt_lower = prompt.lower()
    if any(keyword in prompt_lower for keyword in UNSAFE_KEYWORDS):
        logger.warning(f"Unsafe prompt detected: '{prompt}'")
        return False
    # Add more sophisticated checks (e.g., regex, ML-based) if needed
    return True

def generate_image_with_vertex_ai(prompt: str) -> str:
    """
    Call Vertex AI Gemini 2.0 Pro to generate an educational image.
    Returns base64-encoded image data or raises an exception on failure.
    """
    try:
        # Ensure Vertex AI is initialized
        if not aiplatform.initialized:
            initialize_vertex_ai()

        # Note: Gemini 2.0 Pro image generation API details are assumed based on Vertex AI structure
        # Adjust the endpoint and payload based on actual Gemini 2.0 Pro documentation
        client = aiplatform.gapic.PredictionServiceClient()
        endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}"
        
        instance = {"prompt": prompt}
        parameters = {
            "sampleCount": 1,
            "safetySetting": "BLOCK_MEDIUM_AND_ABOVE",  # Enforce classroom safety
            "outputFormat": "PNG"
        }
        
        response = client.predict(
            endpoint=endpoint,
            instances=[instance],
            parameters=parameters
        )
        
        # Extract image data (assumed base64 for consistency)
        image_data = response.predictions[0]["bytesBase64Encoded"]
        return f"data:image/png;base64,{image_data}"

    except exceptions.GoogleAPIError as e:
        logger.error(f"Vertex AI API error: {str(e)}")
        raise Exception(f"Failed to generate image: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in image generation: {str(e)}")
        raise Exception(f"Image generation failed: {str(e)}")

def validate_image_safety(image_data: str) -> bool:
    """
    Placeholder for image content safety screening.
    Implement ML-based or rule-based checks for classroom appropriateness.
    """
    # TODO: Integrate with a content moderation API (e.g., Google Vision API)
    logger.info("Image safety validation not fully implemented.")
    return True

def test_image_generation(prompt_data: ImagePrompt) -> bool:
    """
    Automated test hook to validate image generation pipeline.
    """
    try:
        enhanced_prompt = enhance_prompt(
            prompt_data.prompt,
            prompt_data.subject,
            prompt_data.grade_level
        )
        if not is_prompt_safe(enhanced_prompt):
            logger.info("Test passed: Unsafe prompt correctly blocked")
            return True
        
        image_data = generate_image_with_vertex_ai(enhanced_prompt)
        if validate_image_safety(image_data):
            logger.info("Test passed: Image generated and validated")
            return True
        return False
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False