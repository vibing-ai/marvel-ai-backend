# test_service_account.py
import os
from google.cloud import storage
from google.cloud import aiplatform
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def test_service_account():
    print("\n=== Testing Google Cloud Service Account ===\n")
    
    # 1. Check if credentials file exists
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    print(f"Checking credentials path: {creds_path}")
    if not creds_path:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS not set in environment!")
        return
        
    if os.path.exists(creds_path):
        print("Credentials file found")
    else:
        print("Credentials file not found!")
        return
    
    # 2. Test Storage Access
    print("\nTesting Storage API...")
    try:
        storage_client = storage.Client()
        bucket_name = "presentation-slide-images"
        bucket = storage_client.bucket(bucket_name)
        
        # Test if bucket exists
        if bucket.exists():
            print(f"Successfully accessed bucket: {bucket_name}")
            
            # Test permissions by trying to list objects
            blobs = list(bucket.list_blobs(max_results=1))
            print(f"Successfully listed bucket contents. Found {len(blobs)} objects")
            if blobs:
                print(f"Example object: {blobs[0].name}")
        else:
            print(f"Bucket {bucket_name} not found!")
            
    except Exception as e:
        print(f"Storage API Error: {str(e)}")
    
    # 3. Test AI Platform
    print("\nTesting AI Platform...")
    try:
        aiplatform.init()
        print("Successfully initialized AI Platform")
    except Exception as e:
        print(f"AI Platform Error: {str(e)}")

if __name__ == "__main__":
    test_service_account()