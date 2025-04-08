from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
from app.models import ImagePrompt, ImageResponse
from app.tools.image_generator.tools import initialize_vertex_ai  # Add this

PROJECT_ID = "eduimagegen"
LOCATION = "us-central1"

def generate_educational_image(prompt_data: ImagePrompt) -> ImageResponse:
    try:
        initialize_vertex_ai(project_id=PROJECT_ID, location=LOCATION)  # Use this
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