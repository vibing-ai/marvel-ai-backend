from typing import List, Optional, Union, Any, Dict
import os
import re
import json
import requests
import base64
import time
import uuid
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from app.services.logger import setup_logger
from langchain_google_genai import GoogleGenerativeAI
from app.api.error_utilities import ImageHandlerError

# Import Google Cloud Storage libraries
try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Set up logging
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
    gcp_url: Optional[str] = Field(None, description="URL to the image stored in GCP bucket (if available)")

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
        verbose: bool = False,
        storage_bucket: Optional[str] = None,
        storage_credentials_path: Optional[str] = None
    ):
        self.args = args
        self.verbose = verbose
        self.model = model or GoogleGenerativeAI(model="gemini-1.5-pro", generation_config={"temperature": 0.7})
        self.prompt_template = read_text_file(prompt_template_path) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), prompt_template_path)) else ""

        # GCP Storage configuration
        self.storage_bucket = storage_bucket or os.environ.get('GCP_STORAGE_BUCKET')
        self.storage_credentials_path = storage_credentials_path or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        self.storage_client = None

        # Initialize GCP storage client if available and configured
        if GCP_AVAILABLE and self.storage_bucket and self.storage_credentials_path:
            try:
                # Check if the credentials file exists at the specified path
                if os.path.exists(self.storage_credentials_path):
                    credentials = service_account.Credentials.from_service_account_file(self.storage_credentials_path)
                    self.storage_client = storage.Client(credentials=credentials)
                    if self.verbose:
                        logger.info(f"GCP Storage client initialized with bucket: {self.storage_bucket}")
                else:
                    logger.warning(f"GCP credentials file not found at: {self.storage_credentials_path}")
            except Exception as e:
                logger.error(f"Error initializing GCP Storage client: {e}")
                self.storage_client = None

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

    def upload_to_gcp_bucket(self, image_data: bytes, prompt: str) -> Optional[str]:
        """Upload an image to a GCP bucket and return the public URL."""
        if not GCP_AVAILABLE or not self.storage_client or not self.storage_bucket:
            if self.verbose:
                logger.info("GCP Storage not available or not configured, skipping upload")
            return None

        try:
            # Generate a unique filename based on timestamp and a UUID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            sanitized_prompt = re.sub(r'[^\w\s-]', '', prompt)[:30].strip().replace(' ', '_')
            filename = f"image_{timestamp}_{sanitized_prompt}_{unique_id}.png"

            # Get the bucket
            bucket = self.storage_client.bucket(self.storage_bucket)

            # Create a new blob and upload the image data
            blob = bucket.blob(f"generated_images/{filename}")
            blob.upload_from_string(image_data, content_type="image/png")

            # Make the blob publicly readable
            blob.make_public()

            # Get the public URL
            public_url = blob.public_url

            if self.verbose:
                logger.info(f"Image uploaded to GCP bucket: {public_url}")

            return public_url

        except Exception as e:
            logger.error(f"Error uploading image to GCP bucket: {e}")
            return None

    def generate_image(self, prompt: str) -> Dict[str, Any]:
        """Generate an image from a prompt using Black Forest Labs Flux 1.1 Pro API."""
        if self.verbose:
            logger.info(f"Generating image with prompt: {prompt}")

        try:
            # Get API key from environment variable or use a default for development
            api_key = os.environ.get('BFL_API_KEY')
            if not api_key:
                logger.warning("BFL_API_KEY environment variable not set. Using development mode.")
                # We return a placeholder in development mode but might want to raise an error here in production
                if self.verbose:
                    logger.info("Development mode: Returning placeholder image data")
                return {
                    "image_b64": "base64_encoded_image_data_would_go_here",
                    "prompt_used": prompt
                }
            else:
                # Log that we have an API key (without revealing it)
                logger.info(f"Using BFL API key: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '****'}")

            # Black Forest Labs API endpoint based on documentation
            url = "https://api.us1.bfl.ai/v1/flux-pro-1.1"
            logger.info(f"Using API endpoint: {url}")

            # Request headers based on documentation
            headers = {
                "accept": "application/json",
                "x-key": api_key,
                "Content-Type": "application/json"
            }

            # Request payload based on documentation
            payload = {
                "prompt": prompt,
                "width": 1024,
                "height": 1024
            }

            logger.info(f"Request payload: width={payload['width']}, height={payload['height']}")

            # Submit the image generation request
            logger.info("Submitting image generation request")
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

                    # Poll for the result with timeout
                    logger.info("Polling for result")
                    result_url = "https://api.us1.bfl.ai/v1/get_result"
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

                                        # Store in GCP bucket if available
                                        gcp_url = None
                                        if GCP_AVAILABLE and self.storage_client:
                                            gcp_url = self.upload_to_gcp_bucket(image_data, prompt)

                                        result = {
                                            "image_b64": image_b64,
                                            "prompt_used": prompt
                                        }

                                        # Add GCP URL to result if available
                                        if gcp_url:
                                            result["gcp_url"] = gcp_url

                                        return result
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

    def detect_content_type(self, prompt, subject=None):
        """
        Detects the type of educational content being requested.
        Returns one of: "diagram", "concept", "process", "historical", "mathematical", "general"
        """
        # Define keyword patterns for each content type
        content_patterns = {
            "diagram": ["diagram", "label", "anatomy", "structure", "cross section", "annotate"],
            "process": ["process", "step", "cycle", "workflow", "sequence", "how to", "stages"],
            "concept": ["concept", "idea", "theory", "principle", "relationship", "compare"],
            "historical": ["historical", "timeline", "era", "period", "ancient", "medieval", "century"],
            "mathematical": ["equation", "formula", "graph", "plot", "function", "geometry", "calculation"]
        }

        # Check the prompt for each pattern
        prompt_lower = prompt.lower()

        # First check subject if provided
        if subject:
            subject_lower = subject.lower()
            if "math" in subject_lower or "algebra" in subject_lower or "geometry" in subject_lower:
                return "mathematical"
            if "history" in subject_lower or "social studies" in subject_lower:
                return "historical"
            if "biology" in subject_lower or "anatomy" in subject_lower:
                return "diagram"
            if "computer science" in subject_lower or "engineering" in subject_lower:
                return "process"

        # Then check prompt keywords
        for content_type, keywords in content_patterns.items():
            if any(keyword in prompt_lower for keyword in keywords):
                logger.info(f"Detected content type: {content_type}")
                return content_type

        # Use AI to detect content type if no clear pattern matches
        try:
            detection_prompt = f"""
            Analyze this educational image request and determine the most appropriate content type.
            Return ONLY one of these exact types: diagram, concept, process, historical, mathematical, general.

            Request: {prompt}
            """

            content_type = self.model.invoke(detection_prompt).strip().lower()

            # Validate the response
            valid_types = ["diagram", "concept", "process", "historical", "mathematical", "general"]
            if content_type in valid_types:
                logger.info(f"AI detected content type: {content_type}")
                return content_type
            else:
                return "general"
        except:
            # Default fallback
            return "general"

    def get_specialized_prompt_template(self, content_type):
        """
        Returns a specialized prompt template based on the detected content type.
        """
        base_prompt = self.prompt_template

        # Specialized additions based on content type
        specialized_sections = {
            "diagram": """
            DIAGRAM DESIGN GUIDELINES:
            - Use precise, accurate labels for all components
            - Employ color-coding to distinguish different parts or systems
            - Include a clear title identifying the diagram's subject
            - Maintain scientific accuracy in proportions and relationships
            - Use callout lines that don't cross when possible
            - Provide a legend if multiple colors/patterns are used
            - Balance detail with clarity - focus on what's educationally relevant
            """,

            "concept": """
            CONCEPT VISUALIZATION GUIDELINES:
            - Use visual metaphors that connect to students' prior knowledge
            - Simplify complex ideas into comprehensible visual forms
            - Show relationships between elements using consistent visual language
            - Limit text to essential terms and definitions
            - Use comparison/contrast where appropriate to highlight distinctions
            - Consider using familiar iconography where applicable
            - Arrange elements to show hierarchy of importance or relationship
            """,

            "process": """
            PROCESS VISUALIZATION GUIDELINES:
            - Create a clear sequential flow with obvious directionality
            - Number steps or use arrows to indicate progression
            - Use consistent visual style for similar process stages
            - Include clear start and end points
            - Differentiate between major and minor steps visually
            - Show cause-and-effect relationships clearly
            - For cyclical processes, ensure the loop is clearly indicated
            """,

            "historical": """
            HISTORICAL CONTENT GUIDELINES:
            - Maintain period-appropriate visual elements and style
            - Emphasize key historical features relevant to learning objectives
            - Use visual cues to indicate time periods or chronology
            - Include contextual elements that aid understanding of historical setting
            - Balance historical accuracy with educational clarity
            - Consider incorporating relevant primary source visual elements
            - Use color and style to distinguish between different eras or regions
            """,

            "mathematical": """
            MATHEMATICAL CONTENT GUIDELINES:
            - Ensure precise representation of mathematical notation and symbols
            - Use consistent scale and proportion in graphs and geometric figures
            - Clearly label axes, points, and other key elements
            - Use colors strategically to highlight mathematical relationships
            - Include grid lines where appropriate for measurement reference
            - Show work or steps for problem-solving where applicable
            - Maintain mathematical accuracy while emphasizing key learning points
            """
        }

        # Default to general guidance if no specialized content is available
        specialized_content = specialized_sections.get(content_type, "")

        return base_prompt + specialized_content

    def generate_educational_image(self) -> ImageGenerationResult:
        """Main method to generate an educational image with all safety checks and enhancements."""
        if not self.args or not self.args.prompt:
            raise ValueError("A prompt is required to generate an image")
        if self.verbose:
            logger.info(f"Generating educational image with prompt: {self.args.prompt}")

        prompt = self.args.prompt
        subject = self.args.subject
        grade_level = self.args.grade_level

        # Check prompt safety
        is_safe = self.check_prompt_safety(prompt)
        if not is_safe:
            raise ImageHandlerError("The prompt contains inappropriate content for educational use", prompt)

        # Detect content type
        content_type = self.detect_content_type(prompt, subject)

        # Get specialized prompt template
        specialized_template = self.get_specialized_prompt_template(content_type)

        # Replace the standard prompt template with the specialized one
        self.prompt_template = specialized_template

        # Enhance prompt with educational context
        context_result = self.enhance_prompt_with_educational_context(prompt, subject, grade_level)
        enhanced_prompt = context_result["enhanced_prompt"]
        educational_context = context_result["educational_context"]

        # Generate the image
        image_result = self.generate_image(enhanced_prompt)

        # Create the result object with all available data
        result_data = {
            "image_b64": image_result["image_b64"],
            "prompt_used": image_result["prompt_used"],
            "educational_context": educational_context,
            "safety_applied": True
        }

        # Add GCP URL to the result if available
        if "gcp_url" in image_result:
            result_data["gcp_url"] = image_result["gcp_url"]

        return ImageGenerationResult(**result_data)