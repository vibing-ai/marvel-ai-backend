from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from app.models import ImagePrompt, ImageResponse
from google.auth import credentials
from google.oauth2 import service_account

PROJECT_ID = "eduimagegen"
LOCATION = "us-central1"
SERVICE_ACCOUNT_KEY_PATH = "C:\\Users\\melis\\OneDrive\\Masaüstü\\marvel-ai-backend\\marvel-ai-backend\\app\\eduimagegen-service-key.json"

def generate_educational_image(prompt_data: ImagePrompt) -> ImageResponse:
    """Generate an educational image description from a text prompt using Gemini 1.5 Pro."""
    try:
        # Load service account credentials
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY_PATH)
        aiplatform.init(project=PROJECT_ID, location=LOCATION, credentials=creds)
        model = GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt_data.prompt)
        text_output = response.text
        return ImageResponse(
            image_url="",
            prompt_used=prompt_data.prompt,
            success=True,
            error_message=f"Text output: {text_output}"
        )
    except Exception as e:
        return ImageResponse(
            image_url="",
            prompt_used=prompt_data.prompt,
            success=False,
            error_message=f"Image generation failed: {str(e)}"
        )