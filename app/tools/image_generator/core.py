from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from app.models import ImagePrompt, ImageResponse
from google.oauth2 import service_account
import logging

PROJECT_ID = "eduimagegen"
LOCATION = "us-central1"
SERVICE_ACCOUNT_KEY_PATH = "C:\\Users\\melis\\OneDrive\\Masaüstü\\marvel-ai-backend\\marvel-ai-backend\\app\\eduimagegen-d664cc7b6af4.json"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_educational_image(prompt_data: ImagePrompt) -> ImageResponse:
    """Generate an educational image description from a text prompt using Gemini 2.0 Pro."""
    try:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_PATH)
        logger.info(f"Initializing Vertex AI with project: {PROJECT_ID}")
        aiplatform.init(project=PROJECT_ID, location=LOCATION, credentials=creds)
        model = GenerativeModel("gemini-2.0-pro")  # Must be gemini-2.0-pro
        response = model.generate_content(prompt_data.prompt)
        text_output = response.text
        return ImageResponse(
            image_url="",
            prompt_used=prompt_data.prompt,
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