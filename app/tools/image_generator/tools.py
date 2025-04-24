import os
import vertexai
import uuid
from io import BytesIO
from vertexai.preview.vision_models import ImageGenerationModel
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.logger import setup_logger
from langchain_google_genai import GoogleGenerativeAI
from app.services.firebase import FirebaseManager


logger = setup_logger(__name__)

class ImageGenerationError(Exception):
    """Custom exception for image generation errors"""
    pass


def read_prompt_file(prompt_name: str, verbose: bool = False) -> str:
    """ Reads a prompt file from the prompt directory."""
    try:
        # Get the directory containing the script file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to prompt file in the prompt directory
        prompt_path = os.path.join(script_dir, "prompt", prompt_name)
            
        with open(prompt_path, 'r', encoding='utf-8') as file:
            content = file.read()          
        return content
        
    except FileNotFoundError:
        error_msg = f"Prompt file not found: {prompt_name}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    except IOError as e:
        error_msg = f"Error reading prompt file {prompt_name}: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)


def check_prompt_safety(base_prompt: str, grade_level: str, subject: str, api_key: str, verbose: bool = False) -> tuple[bool, str]:
    try:
        # Read safety check prompt template
        safety_prompt_template = read_prompt_file("check_prompt.txt", verbose)

        # Compose the full safety check prompt
        safety_prompt = safety_prompt_template.format(
            prompt=base_prompt,
            grade_level=grade_level,
            subject=subject
        )

        if verbose:
            logger.info(f"Checking prompt safety using Gemini")

        # Initialize Gemini model for safety check
        safety_model = GoogleGenerativeAI(
            model="gemini-2.0-flash-001",
            max_output_tokens=100,
            api_key=api_key
        )

        # Get safety check response
        response = safety_model.generate([safety_prompt])
        result = response.generations[0][0].text.strip().lower()

        # Parse response
        is_safe = "safe" in result and "unsafe" not in result
        
        if verbose:
            logger.info(f"Safety check result: {result}")

        return is_safe, result

    except Exception as e:
        error_message = f"Error in prompt safety check: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

def map_language(user_language: str | None = None) -> str:
    if not user_language:
        return "en"
    return {
        "English": "en",
        "Hindi":   "hi",
        "Japanese":"ja",
        "Korean":  "ko",
    }.get(user_language, "en")

def save_to_cloud_storage(generated_image):
    """Save the image to Google Cloud Storage"""
    firebase_manager = FirebaseManager()
    image_url = firebase_manager.upload_image(generated_image, f"images/{uuid.uuid4()}.png")        
    logger.info(f"Image uploaded to Firebase")
    return image_url

def executor_image_generator(base_prompt: str, grade_level: str, subject: str,
                             api_key: str, project_id: str, language: str | None = None, verbose: bool = False) -> dict:
    
    try:

        # Perform safety check
        is_safe, safety_message = check_prompt_safety(base_prompt, grade_level, subject, api_key, verbose)
        if not is_safe:
            logger.error(f"Unsafe prompt detected: {safety_message}")
            raise ValueError(f"Unsafe prompt: {safety_message}")

        # Read enhancement prompt template and positive/negative prompts
        enhancement_template = read_prompt_file("enhancement.txt", verbose)
        positive_prompt = read_prompt_file("prompt_positive.txt", verbose)
        negative_prompt = read_prompt_file("prompt_negative.txt", verbose)

        # Compose the full enhancement prompt
        full_prompt = enhancement_template.format(
            prompt=base_prompt,
            grade_level=grade_level,
            subject=subject,
            language=language
        )

        if verbose:
            logger.info(f"Enhancing prompt using Gemini")

        # Generate enhanced prompt using Gemini
        gemini_model = GoogleGenerativeAI(
            model="gemini-2.0-flash-001", 
            max_output_tokens=280,
            api_key=api_key
        )

        generated_results = gemini_model.generate([full_prompt])
        enhanced_prompt = generated_results.generations[0][0].text.strip()
        logger.info(f"Enhanced prompt received: {enhanced_prompt}")
        
        # Combine enhanced prompt with positive instructions
        final_prompt = f"{enhanced_prompt}\n\n{positive_prompt}"
        

        # Initialize Vertex AI and generate image using imagen-3.0-generate-002
        vertexai.init(project=project_id, location="us-central1")
        Image_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        logger.info("Generating image using Vertex AI's imagen-3.0-generate-002")

        image_response = Image_model.generate_images(
            prompt=final_prompt,
            negative_prompt=negative_prompt,
            number_of_images=1,
            language=map_language(language),
            aspect_ratio="1:1",
            safety_filter_level="block_only_high",
            person_generation="allow_adult",
        )
        
        if not image_response or not image_response.images or len(image_response.images) == 0:
            error_message = (
                "Model did not return any images. This may happen if:\n"
                "- The prompt was flagged as unsafe by the model's internal safety filters.\n"
                "- The prompt involves generating images of children (e.g., 'students', 'kids'), "
                "Consider rephrasing the prompt to exclude references to minors."
            )
            
            logger.error(error_message)
            raise ValueError(error_message)
            
        # Get the generated image
        generated_image = image_response.images[0]
        
        # Upload to cloud storage
        try:
            image_url = save_to_cloud_storage(generated_image)
            return {
                "image_url": image_url,
            }
        except Exception as e:
            logger.error(f"Failed to save image to cloud storage: {str(e)}", exc_info=True)
            raise ImageGenerationError(f"Image generated but storage failed: {str(e)}")

    except LoaderError as e:
        error_message = f"LoaderError in Image Generator Pipeline -> {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except Exception as e:
        logger.error(f"Error in image generation pipeline: {str(e)}")
        raise ValueError(f"Image generation failed: {str(e)}")
