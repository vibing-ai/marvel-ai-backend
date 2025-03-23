# test_service_account.py
import os
import io
from pathlib import Path
from PIL import Image
from google.cloud import storage
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from dotenv import load_dotenv

# Find the project root directory and load environment variables
current_file = Path(__file__)
project_root = current_file.parent
# Navigate up until we find the project root (where the app directory is)
while not (project_root / 'app').exists() and project_root != project_root.parent:
    project_root = project_root.parent

# Look for .env in common locations
env_paths = [
    project_root / 'app' / '.env',  # app/.env
    project_root / '.env',          # .env in project root
]

# Try to load from the first .env file found
env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        print(f"Loading environment from: {env_path}")
        load_dotenv(env_path)
        env_loaded = True
        break

if not env_loaded:
    print("Warning: No .env file found. Using environment variables as is.")

def test_service_account():
    print("\n=== Testing Google Cloud Service Account ===\n")
    
    # 1. Find and verify credentials
    print("Step 1: Finding credentials file")
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Make relative path absolute if needed
    if creds_path and not os.path.isabs(creds_path):
        creds_path = os.path.join(project_root, creds_path)
    
    # Use default location if not specified
    if not creds_path:
        creds_path = project_root / 'marvel-ai-backend-credentials.json' # as per your credentials file name
    
    # Check if file exists
    if os.path.exists(creds_path):
        print(f"✅ Credentials file found at: {creds_path}")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(creds_path)
    else:
        print(f"❌ Credentials file not found at: {creds_path}")
        return
    
    # 2. Generate a test image with Vertex AI
    print("\nStep 2: Generating test image with Vertex AI")
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        print("❌ PROJECT_ID not set in environment")
        return
    
    print(f"Initializing Vertex AI with project: {project_id}")
    vertexai.init(project=project_id)
    
    # Generate a simple test image
    print("Generating image...")
    image_model = ImageGenerationModel.from_pretrained("imagen-3.0-fast-generate-001")
    prompt = "A simple blue circle on a white background, abstract, no text"
    
    try:
        response = image_model.generate_images(
            prompt=prompt,
            number_of_images=1,
        )
        
        if response and hasattr(response[0], '_image_bytes'):
            image_bytes = response[0]._image_bytes
            print(f"✅ Successfully generated image ({len(image_bytes)} bytes)")
            
            # Save image locally for verification
            with open("test_image.png", "wb") as f:
                f.write(image_bytes)
            print("✅ Saved test image to test_image.png")
        else:
            print("❌ Failed to generate image")
            return
    except Exception as e:
        print(f"❌ Image generation error: {str(e)}")
        return
    
    # 3. Store the image in Cloud Storage
    print("\nStep 3: Storing image in Cloud Storage")
    bucket_name = os.getenv('SLIDE_IMAGES_BUCKET_NAME', 'presentation-slide-images')
    print(f"Using bucket: {bucket_name}")
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # Upload the generated image
        blob = bucket.blob("test_image.png")
        blob.upload_from_string(image_bytes, content_type="image/png")
        print(f"✅ Successfully uploaded image to: gs://{bucket_name}/test_image.png")
        
        # Make it publicly accessible and get URL
        blob.make_public()
        print(f"✅ Public URL: {blob.public_url}")
        
        # Clean up (optional)
        # blob.delete()
        # print("✅ Deleted test image from bucket")
        
    except Exception as e:
        print(f"❌ Storage error: {str(e)}")

if __name__ == "__main__":
    test_service_account()