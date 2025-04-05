# FLUX API Setup Guide using Together.ai

## Overview
FLUX is an image generation model available through Together.ai's platform. This guide will walk you through setting up and using the FLUX API for image generation.

## Prerequisites

### 1. Together.ai Account Setup
1. Visit [Together.ai](https://api.together.xyz/signup)
2. Create a new account or sign in
3. Navigate to [API Settings](https://api.together.xyz/settings/api-keys)
4. Generate a new API key
5. Copy and save your API key securely

### 2. Environment Setup
Add your Together.ai API key to your `.env` file:
```env
TOGETHER_API_KEY=your_together_api_key
```

## Installation

Install the Together.ai Python package:
```bash
pip install together
```

## Basic Usage

### 1. Initialize the Together Client
```python
from together import Together

client = Together(
    api_key="your_together_api_key"  # Or will use TOGETHER_API_KEY from environment
)
```

### 2. Generate Images
```python
response = client.images.generate(
    prompt="your image description",
    model="stabilityai/stable-diffusion-xl-base-1.0",  # or other supported models
    steps=30,  # number of inference steps
    width=1024,  # image width
    height=1024,  # image height
    seed=42,  # optional: for reproducible results
    n=1  # number of images to generate
)

# The response contains base64 encoded images
image_data = response.data[0].b64_json
```

## Advanced Configuration

### 1. Model Selection
FLUX supports various models. Common options include:
- `stabilityai/stable-diffusion-xl-base-1.0`
- `stabilityai/sdxl-turbo`
- `stabilityai/stable-diffusion-2-1`

### 2. Generation Parameters
```python
response = client.images.generate(
    prompt="detailed prompt here",
    model="stabilityai/stable-diffusion-xl-base-1.0",
    steps=30,
    width=1024,
    height=1024,
    n=1,
    negative_prompt="things to avoid in generation",
    guidance_scale=7.5,  # Controls how closely to follow the prompt
    seed=42,
    scheduler="dpm++",  # Sampling method
)
```

### 3. Error Handling
```python
from together import TogetherException

try:
    response = client.images.generate(
        prompt="your prompt",
        model="stabilityai/stable-diffusion-xl-base-1.0"
    )
except TogetherException as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"General Error: {e}")
```

## Best Practices

### 1. Prompt Engineering
- Be specific and detailed in your prompts
- Use descriptive adjectives
- Specify art style if desired
- Include technical details (e.g., "high resolution", "detailed")

Example:
```python
prompt = """
A majestic mountain landscape at sunset, 
ultra-detailed, golden hour lighting, 
atmospheric perspective, high resolution, 
cinematic composition, 8k quality
"""
```

### 2. Rate Limiting and Quotas
- Monitor your API usage through Together.ai dashboard
- Implement retry logic for failed requests
- Consider batch processing for multiple images

### 3. Image Storage
- Save generated images immediately
- Implement proper error handling for failed generations
- Consider implementing a caching system

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Errors**
   - Verify API key is correct
   - Check environment variable is properly set
   - Ensure API key has not expired

2. **Generation Failures**
   - Check prompt length and content
   - Verify model name is correct
   - Confirm parameters are within acceptable ranges

3. **Quality Issues**
   - Increase steps parameter
   - Adjust guidance_scale
   - Refine prompt with more details
   - Try different models

## API Response Structure
```python
{
    'data': [{
        'b64_json': 'base64_encoded_image_data',
        'seed': 123456,
        'model': 'stabilityai/stable-diffusion-xl-base-1.0'
    }],
    'created': 1234567890
}
```

## Environment Variables Summary
```env
TOGETHER_API_KEY=your_api_key_here
TOGETHER_BASE_URL=https://api.together.xyz  # Optional, defaults to this
```

## Additional Resources
- [Together.ai Documentation](https://docs.together.ai/docs/inference-image)
- [API Reference](https://docs.together.ai/reference/images_v1_generate)
- [Model List](https://docs.together.ai/docs/inference-models)