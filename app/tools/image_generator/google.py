from google.cloud import aiplatform
import os
from app.services.logger import setup_logger
logger = setup_logger(__name__)

# Initialize Vertex AI
aiplatform.init(project= os.environ.get('PROJECT_ID'), location="us-central1")

# Load the Image Generation Model
image_generation_model = aiplatform.GenerativeModel(model_name="imagegeneration") # Or the specific model you are using

def generate_image(self):
    """Main image generation pipeline with Vertex AI safety checks"""
    try:
        # Step 1: Enhance prompt with educational context
        enhanced_prompt = self.enhance_prompt()
        if not enhanced_prompt or not enhanced_prompt.get("image_prompt"):
            raise ValueError("Failed to generate a valid enhanced prompt with image_prompt")

        image_prompt = enhanced_prompt["image_prompt"]

        # Step 2: Configure Safety Settings
        safety_config = {
            "categories": [
                "HARM_CATEGORY_DEROGATORY",
                "HARM_CATEGORY_TOXICITY",
                "HARM_CATEGORY_VIOLENCE",
                "HARM_CATEGORY_SEXUAL",
                "HARM_CATEGORY_MEDICAL",
                "HARM_CATEGORY_DANGEROUS",
            ],
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",  # Or "BLOCK_LOW_AND_ABOVE", "BLOCK_ONLY_HIGH", "ALLOW_ALL"
        }

        # Step 3: Generate Images with Safety Configuration
        response = self.image_generator_model.generate_images(
            prompt=image_prompt,
            number_of_images=1,
            safety_config=safety_config,
            # Optional parameters like seed, add_watermark, etc.
        )

        if response.images:
            generated_image = response.images[0]
            logger.info("Generated image successfully.")
            generated_image.save("generated_image.png")
            return enhanced_prompt
        else:
            logger.warning("Image generation returned no images, likely due to safety filters.")
            return None

    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        return None