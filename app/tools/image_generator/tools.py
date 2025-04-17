from typing import List, Optional, Union, Any, Dict
import os
import re
import json
import requests
import base64
import time
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from app.services.logger import setup_logger
from langchain_google_genai import GoogleGenerativeAI
from app.api.error_utilities import ImageHandlerError

# Load environment variables from .env file
load_dotenv(find_dotenv())

logger = setup_logger(__name__)

def read_text_file(file_path):
    """Read text from a file relative to the current script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()

class ImageGenerationResult(BaseModel):
    """Model for the image generation result."""
    image_b64: str = Field(..., description="Base64 encoded image data")
    prompt_used: str = Field(..., description="The actual prompt used to generate the image")
    educational_context: str = Field(..., description="The educational context that was applied")
    safety_applied: bool = Field(..., description="Whether safety filtering was applied")

class ImageGeneratorArgs(BaseModel):
    """Arguments for the image generator."""
    prompt: str = Field(..., description="The text prompt to generate an image from")
    subject: Optional[str] = Field(None, description="The educational subject (e.g., 'math', 'science')")
    grade_level: Optional[str] = Field(None, description="The grade level (e.g., 'elementary', 'middle school', 'high school')")
    lang: str = Field("en", description="The language for text in the image")

class ImageGenerator:
    """Main class for generating educational images from text prompts."""

    def __init__(
        self,
        args: Optional[ImageGeneratorArgs] = None,
        model = None,
        prompt_template_path: str = "prompt/image-generator-prompt.txt",
        verbose: bool = False
    ):
        self.args = args
        self.verbose = verbose
        # For safety checks and context enhancement, we'll use Google's Gemini model
        self.model = model or GoogleGenerativeAI(model="gemini-1.5-pro", generation_config={"temperature": 0.7})
        # We won't be using the image_model for Flux implementation
        # self.image_model = ChatGoogleGenerativeAI(model="gemini-2.0-pro-vision")
        self.prompt_template = read_text_file(prompt_template_path) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), prompt_template_path)) else ""

        if self.verbose:
            logger.info(f"ImageGenerator initialized with args: {args}")

    def enhance_prompt_with_educational_context(self, prompt: str, subject: Optional[str] = None, grade_level: Optional[str] = None) -> Dict[str, str]:
        """Enhance the prompt with educational context."""
        if self.verbose:
            logger.info(f"Enhancing prompt with educational context. Original prompt: {prompt}")

        # If subject and grade_level are provided, use them directly
        if subject and grade_level:
            enhanced_prompt = f"{prompt}, educational context: {subject} for {grade_level} level"
            return {
                "enhanced_prompt": enhanced_prompt,
                "educational_context": f"{subject} for {grade_level} level"
            }

        # Otherwise, use Gemini to infer the educational context
        try:
            context_prompt = f"""
            Analyze this image generation prompt and determine the most appropriate educational subject
            and grade level. Return ONLY a JSON with two fields: 'subject' and 'grade_level'.

            Prompt: {prompt}

            Example response format:
            {{
                "subject": "biology",
                "grade_level": "middle school"
            }}
            """

            response = self.model.invoke(context_prompt)

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                import json
                try:
                    context_data = json.loads(json_match.group(0))
                    inferred_subject = context_data.get("subject", "general education")
                    inferred_grade_level = context_data.get("grade_level", "all levels")

                    enhanced_prompt = f"{prompt}, educational context: {inferred_subject} for {inferred_grade_level} level"

                    if self.verbose:
                        logger.info(f"Inferred educational context: {inferred_subject} for {inferred_grade_level}")

                    return {
                        "enhanced_prompt": enhanced_prompt,
                        "educational_context": f"{inferred_subject} for {inferred_grade_level} level"
                    }
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from context inference")

            # Fallback if JSON parsing fails
            enhanced_prompt = f"{prompt}, educational context: suitable for classroom use"
            return {
                "enhanced_prompt": enhanced_prompt,
                "educational_context": "general educational content"
            }

        except Exception as e:
            logger.error(f"Error enhancing prompt with educational context: {e}")
            # Fallback to original prompt with basic educational context
            enhanced_prompt = f"{prompt}, educational context: suitable for classroom use"
            return {
                "enhanced_prompt": enhanced_prompt,
                "educational_context": "general educational content"
            }

    def check_prompt_safety(self, prompt: str) -> bool:
        """Check if the prompt is safe for educational use."""
        if self.verbose:
            logger.info(f"Checking prompt safety: {prompt}")

        # List of unsafe keywords or topics to filter
        unsafe_keywords = [
            "nude", "naked", "pornographic", "sexual", "violence", "gore", "drugs", "suicide",
            "self-harm", "terrorism", "hate speech", "racist", "sexist", "discriminatory"
        ]

        # Simple keyword check
        lower_prompt = prompt.lower()
        for keyword in unsafe_keywords:
            if keyword in lower_prompt:
                logger.warning(f"Unsafe keyword detected in prompt: {keyword}")
                return False

        # Use Gemini for more sophisticated safety check
        try:
            safety_prompt = f"""
            Analyze this image generation prompt and determine if it's safe and appropriate for educational use.
            Return ONLY "SAFE" or "UNSAFE".

            Prompt: {prompt}
            """

            response = self.model.invoke(safety_prompt).strip().upper()

            if "UNSAFE" in response:
                logger.warning(f"AI model determined prompt is unsafe: {prompt}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking prompt safety: {e}")
            # Default to allowing the prompt if the safety check fails
            return True

    def generate_image(self, prompt: str) -> Dict[str, Any]:
        """Generate an image from a prompt using Black Forest Labs Flux 1.1 Pro API."""
        if self.verbose:
            logger.info(f"Generating image with prompt: {prompt}")

        try:
            # Get API key from environment variable or use a default for development
            api_key = os.environ.get('BFL_API_KEY')
            if not api_key:
                logger.warning("BFL_API_KEY environment variable not set. Using development mode.")
                # In a real implementation, you might want to raise an error here
                # For now, we'll return a placeholder in development mode
                if self.verbose:
                    logger.info("Development mode: Returning placeholder image data")
                return {
                    "image_b64": "base64_encoded_image_data_would_go_here",
                    "prompt_used": prompt
                }
            else:
                # Log that we have an API key (without revealing it)
                logger.info(f"Using BFL API key: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '****'}")

            # Updated Black Forest Labs API endpoint based on documentation
            url = "https://api.us1.bfl.ai/v1/flux-pro-1.1"
            logger.info(f"Using API endpoint: {url}")

            # Updated request headers based on documentation
            headers = {
                "accept": "application/json",
                "x-key": api_key,
                "Content-Type": "application/json"
            }

            # Updated request payload based on documentation
            payload = {
                "prompt": prompt,
                "width": 1024,
                "height": 1024
            }

            logger.info(f"Request payload: width={payload['width']}, height={payload['height']}")

            # Step 1: Submit the image generation request
            logger.info("Step 1: Submitting image generation request")
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            # Log the response status and headers for debugging
            logger.info(f"Response status code: {response.status_code}")

            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Response data keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dictionary'}")

                # Extract the request ID
                if 'id' in response_data:
                    request_id = response_data['id']
                    logger.info(f"Request ID: {request_id}")

                    # Step 2: Poll for the result
                    logger.info("Step 2: Polling for result")
                    result_url = "https://api.us1.bfl.ai/v1/get_result"

                    # Poll for the result with timeout
                    max_attempts = 30  # Maximum number of polling attempts
                    poll_interval = 1  # Seconds between polling attempts

                    for attempt in range(max_attempts):
                        logger.info(f"Polling attempt {attempt + 1}/{max_attempts}")

                        result_response = requests.get(
                            result_url,
                            headers={
                                "accept": "application/json",
                                "x-key": api_key
                            },
                            params={
                                "id": request_id
                            },
                            timeout=10
                        )

                        if result_response.status_code == 200:
                            result_data = result_response.json()
                            logger.info(f"Result status: {result_data.get('status')}")

                            if result_data.get("status") == "Ready":
                                # Get the image URL
                                image_url = result_data.get("result", {}).get("sample")

                                if image_url:
                                    logger.info(f"Image URL: {image_url}")

                                    # Download the image and convert to base64
                                    image_response = requests.get(image_url, timeout=10)
                                    if image_response.status_code == 200:
                                        image_data = image_response.content
                                        image_b64 = base64.b64encode(image_data).decode('utf-8')

                                        logger.info("Image generated and converted to base64 successfully")

                                        return {
                                            "image_b64": image_b64,
                                            "prompt_used": prompt
                                        }
                                    else:
                                        error_msg = f"Failed to download image from URL: {image_url}, status code: {image_response.status_code}"
                                        logger.error(error_msg)
                                        raise ImageHandlerError(error_msg, prompt)
                                else:
                                    error_msg = "No image URL in the result data"
                                    logger.error(error_msg)
                                    raise ImageHandlerError(error_msg, prompt)
                            elif result_data.get("status") == "Failed":
                                error_msg = f"Image generation failed: {result_data.get('error', 'Unknown error')}"
                                logger.error(error_msg)
                                raise ImageHandlerError(error_msg, prompt)
                            else:
                                # Still processing, wait and try again
                                logger.info(f"Status: {result_data.get('status')}, waiting {poll_interval} seconds...")
                                time.sleep(poll_interval)
                        else:
                            error_msg = f"Failed to get result, status code: {result_response.status_code}"
                            logger.error(error_msg)
                            raise ImageHandlerError(error_msg, prompt)

                    # If we get here, we've exceeded the maximum number of polling attempts
                    error_msg = f"Exceeded maximum polling attempts ({max_attempts})"
                    logger.error(error_msg)
                    raise ImageHandlerError(error_msg, prompt)
                else:
                    error_msg = "No request ID in the response data"
                    logger.error(error_msg)
                    raise ImageHandlerError(error_msg, prompt)
            else:
                error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                logger.error(error_msg)
                # Try to parse the error response for more details
                try:
                    error_json = response.json()
                    logger.error(f"Detailed error response: {error_json}")
                except:
                    logger.error("Could not parse error response as JSON")
                raise ImageHandlerError(error_msg, prompt)

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise ImageHandlerError(f"Failed to generate image: {str(e)}", prompt)

    def generate_educational_image(self) -> ImageGenerationResult:
        """Main method to generate an educational image with all safety checks and enhancements."""
        if not self.args or not self.args.prompt:
            raise ValueError("A prompt is required to generate an image")

        prompt = self.args.prompt
        subject = self.args.subject
        grade_level = self.args.grade_level

        # Check prompt safety
        is_safe = self.check_prompt_safety(prompt)
        if not is_safe:
            raise ImageHandlerError("The prompt contains inappropriate content for educational use", prompt)

        # Enhance prompt with educational context
        context_result = self.enhance_prompt_with_educational_context(prompt, subject, grade_level)
        enhanced_prompt = context_result["enhanced_prompt"]
        educational_context = context_result["educational_context"]

        # Generate the image
        image_result = self.generate_image(enhanced_prompt)

        # Return the result
        return ImageGenerationResult(
            image_b64=image_result["image_b64"],
            prompt_used=image_result["prompt_used"],
            educational_context=educational_context,
            safety_applied=True
        )