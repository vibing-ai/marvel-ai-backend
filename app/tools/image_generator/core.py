from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from app.models import ImagePrompt, ImageResponse

PROJECT_ID = "eduimagegen"
LOCATION = "us-central1"

def generate_educational_image(prompt_data: ImagePrompt) -> ImageResponse:
    """Generate an educational image description from a text prompt using Gemini 1.5 Pro."""
    try:
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel("gemini-1.5-pro")  # Stable model
        response = model.generate_content(prompt_data.prompt)
        text_output = response.text
        return ImageResponse(
            image_url="",  # Text-only for now
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