from google.cloud import aiplatform
from app.models import ImagePrompt, ImageResponse
from app.tools.image_generator.tools import initialize_vertex_ai

PROJECT_ID = "eduimagegen"
LOCATION = "us-central1"

def generate_educational_image(prompt_data: ImagePrompt) -> ImageResponse:
    """Generate an educational image from a text prompt using Vertex AI and Gemini 2.5 Pro."""
    try:
        initialize_vertex_ai(project_id=PROJECT_ID, location=LOCATION)
        endpoint = aiplatform.Endpoint(
            endpoint_name="projects/eduimagegen/locations/us-central1/endpoints/3059040360077459456"  # Your ENDPOINT_ID
        )
        request_payload = {
            "instances": [{"prompt": prompt_data.prompt}],
            "parameters": {"sampleCount": 1}  # Text-only for now
        }
        response = endpoint.predict(**request_payload).predictions[0]
        text_output = response if isinstance(response, str) else response.get("text", "")
        return ImageResponse(
            image_url="",  # Text-only model
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