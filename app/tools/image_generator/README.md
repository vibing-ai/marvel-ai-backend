# Image Generator

This tool generates high-quality educational images from text prompts using Black Forest Labs' Flux 1.1 Pro model and automatically stores them in Google Cloud Storage for persistent access.

## Features

- Generate educational images from text prompts
- Enhance prompts with educational context
- Safety filtering to ensure appropriate content
- Integration with Black Forest Labs Flux 1.1 Pro API
- Automatic storage in Google Cloud Storage (when configured)
- Content type detection (diagrams, concepts, processes, etc.)

## Setup

1. Install the required dependencies:
   ```
   # From the marvel-ai-backend directory
   pip install -r requirements.txt
   ```

   Note: All required dependencies are included in the main project's requirements.txt file.

2. Set up your Black Forest Labs API key in the .env file:

   Add the following line to your `.env` file in the `marvel-ai-backend/app/` directory:
   ```
   BFL_API_KEY=your_api_key_here
   ```

   You can obtain an API key by registering at [api.bfl.ml](https://api.bfl.ml/).

3. Set up Google Cloud Storage for image persistence:

   a. Create a storage bucket in the GCP project associated with the PROJECT_ID environment variable in your .env file (see GCP Storage Configuration below)

   b. Add the following to your `.env` file:
   ```
   GCP_STORAGE_BUCKET=your-gcp-bucket-name
   GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/your/credentials.json
   ```

4. When running in Docker, mount the credentials file:

   ```bash
   docker run \
     -v /path/to/credentials.json:/app/credentials.json:ro \
     -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
     -p 8000:8000 \
     --env-file ./app/.env \
     your-image-name
   ```

## Usage

### API Request Format

```json
{
  "user": {
    "id": "string",
    "fullName": "string",
    "email": "string"
  },
  "type": "tool",
  "tool_data": {
    "tool_id": "image-generator",
    "inputs": [
      {
        "name": "prompt",
        "value": "A diagram of the solar system"
      },
      {
        "name": "subject",
        "value": "astronomy"
      },
      {
        "name": "grade_level",
        "value": "middle school"
      },
      {
        "name": "lang",
        "value": "en"
      }
    ]
  }
}
```

### Input Parameters

- `prompt` (required): The text prompt to generate an image from
- `subject` (optional): The educational subject (e.g., 'math', 'science')
- `grade_level` (optional): The grade level (e.g., 'elementary', 'middle school', 'high school')
- `lang` (optional, default: "en"): The language for text in the image

### Response Format

```json
{
  "image_b64": "base64_encoded_image_data",
  "prompt_used": "A diagram of the solar system, educational context: astronomy for middle school level",
  "educational_context": "astronomy for middle school level",
  "safety_applied": true,
  "gcp_url": "https://storage.googleapis.com/your-bucket/generated_images/image_20250422_123456_solar_system_abcd1234.png"
}
```

The `gcp_url` field will be included if GCP storage is configured and the image was successfully uploaded.

## Implementation Details

The image generator uses Black Forest Labs' Flux 1.1 Pro model, which is a state-of-the-art text-to-image model. The tool enhances the prompt with educational context and applies safety filtering to ensure the generated images are appropriate for educational use.

## Dependencies

- requests
- Pillow
- langchain-google-genai
- pydantic
- google-cloud-storage (for GCP integration)

## GCP Storage Configuration

### Creating a GCP Bucket

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "Cloud Storage" > "Buckets"
3. Click "CREATE BUCKET"
4. Enter a globally unique name
5. Choose your preferred region
6. Set access control to "Fine-grained"
7. Click "CREATE"

### Setting Bucket Permissions

1. Click on your newly created bucket
2. Go to the "Permissions" tab
3. Click "GRANT ACCESS"
4. Enter `allUsers` in the "New principals" field
5. Select "Cloud Storage" > "Storage Object Viewer" for the role
6. Click "SAVE"

### Creating a Service Account

1. Navigate to "IAM & Admin" > "Service Accounts"
2. Click "CREATE SERVICE ACCOUNT"
3. Enter a name and description
4. Add the "Storage Object Admin" role
5. Create a key (JSON format)
6. Download the key file

### Troubleshooting GCP Storage

- Check that your service account has the correct permissions
- Verify that the credentials file path is correct and accessible
- Ensure the bucket exists and is publicly readable
- Check the logs for detailed error messages
- When using Docker, make sure the credentials file is mounted correctly
