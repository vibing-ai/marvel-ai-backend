# Image Generator Setup Guide

## Prerequisites

1. **API Keys and Credentials**
   - Together.ai API key (for FLUX.1-schnell model)
   - Google AI Studio API key (for Gemini-1.5-pro model)
   - Google Cloud Project credentials (for GCS storage)

2. **Environment Variables**
   Create a `.env` file with:
   ```
   TOGETHER_API_KEY=your_together_api_key
   GOOGLE_API_KEY=your_google_ai_studio_key
   GOOGLE_CLOUD_PROJECT=your-project-id
   GCS_BUCKET_NAME=your-bucket-name
   ```

3. **Google Cloud Setup**
   - Create a Google Cloud Project
   - Enable Cloud Storage API
   - Create a service account with the following IAM roles:
     * `roles/storage.admin` (Storage Admin) - Full control of GCS resources
     * `roles/storage.objectViewer` - Read access to bucket objects
     * `roles/storage.objectCreator` - Ability to create new objects
     * `roles/storage.buckets.get` - Ability to get bucket metadata
     
     You can add these roles through the Google Cloud Console:
     1. Go to IAM & Admin > Service Accounts
     2. Select your service account
     3. Click "EDIT" (pencil icon)
     4. Click "ADD ANOTHER ROLE"
     5. Add each of the roles listed above
   - Download service account key JSON file
   - Set local-start.sh/GOOGLE_APPLICATION_CREDENTIALS environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
     ```

4. **Required Files**
   Ensure these prompt template files exist:
   ```
   marvel-ai-backend/app/tools/presentation_generator_updated/image_generator/prompt/
   ├── visual_prompt.txt
   └── theme_prompt.txt
   ```

5. **Python Dependencies**
   ```bash
   pip install together langchain-google-genai google-cloud-storage
   ```

## Configuration Checklist

- [ ] Together.ai API key configured
- [ ] Google AI Studio API key set up
- [ ] GCS bucket created and configured
- [ ] Service account credentials set up
- [ ] Prompt template files in place
- [ ] Environment variables set

## Troubleshooting

- If images fail to generate: Check Together.ai API key and quota
- If storage fails: Verify GCS permissions and bucket existence
- If prompt generation fails: Check Google AI Studio API key and quota
