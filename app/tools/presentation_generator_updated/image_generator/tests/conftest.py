import pytest
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables needed for testing"""
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
    os.environ['GCS_BUCKET_NAME'] = 'test-bucket'
    os.environ['OPENAI_API_KEY'] = 'test-key'

@pytest.fixture
def mock_gcs_client():
    """Mock Google Cloud Storage client"""
    class MockGCSClient:
        def bucket(self, name):
            return MockBucket()
    
    class MockBucket:
        def blob(self, name):
            return MockBlob()
    
    class MockBlob:
        def upload_from_string(self, data, content_type):
            pass
        
        def public_url(self):
            return "https://storage.googleapis.com/test-bucket/test-image.jpg"
    
    return MockGCSClient()