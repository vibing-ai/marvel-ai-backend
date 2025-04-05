import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_CLOUD_PROJECT = os.getenv('PROJECT_ID')
    GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')