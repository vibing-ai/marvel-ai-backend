import os
from google.cloud import aiplatform
from google.api_core import exceptions

# Exact path to key (Windows format)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\melis\\OneDrive\\Masaüstü\\marvel-ai-backend\\marvel-ai-backend\\app\\eduimagegen-d664cc7b6af4.json"

def initialize_vertex_ai(project_id: str, location: str = "us-central1") -> None:
    """Initialize Vertex AI with service account credentials."""
    try:
        # Updated init call
        aiplatform.init(
            project=project_id,  # Use 'project' instead of 'project_id'
            location=location
        )
        print("Vertex AI initialized successfully.")
    except exceptions.GoogleAPIError as e:
        raise Exception(f"Failed to initialize Vertex AI: {str(e)}")