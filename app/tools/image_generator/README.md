# Image Generator

This tool generates high-quality educational images from text prompts using Black Forest Labs' Flux 1.1 Pro model.

## Features

- Generate educational images from text prompts
- Enhance prompts with educational context
- Safety filtering to ensure appropriate content
- Integration with Black Forest Labs Flux 1.1 Pro API

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
  "safety_applied": true
}
```

## Implementation Details

The image generator uses Black Forest Labs' Flux 1.1 Pro model, which is a state-of-the-art text-to-image model. The tool enhances the prompt with educational context and applies safety filtering to ensure the generated images are appropriate for educational use.

## Dependencies

- requests
- Pillow
- langchain-google-genai
- pydantic
