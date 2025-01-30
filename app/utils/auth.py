from fastapi import HTTPException, Header
from google.cloud import secretmanager
import os

def access_secret_file(secret_id, version_id="latest"):
    """
    Access a secret file in Google Cloud Secret Manager and parse it.
    """
    project_id = os.environ.get('PROJECT_ID')
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

# Function to ensure incoming request is from controller with key
def key_check(api_key: str = Header(None)):
  
  if os.environ['ENV_TYPE'] == "production":
    set_key = access_secret_file("backend-access")
  else:
    set_key = "dev"
  
  if api_key is None or api_key != set_key:
    raise HTTPException(status_code=401, detail="Invalid API Request Key")