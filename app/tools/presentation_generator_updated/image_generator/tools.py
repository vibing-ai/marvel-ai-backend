import os
import time
import uuid
from datetime import datetime
from io import BytesIO
from typing import Union, List, Dict, Any

import replicate
from google.cloud import storage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from vertexai.preview.vision_models import ImageGenerationModel

from app.services.logger import setup_logger

logger = setup_logger(__name__)

# Dictionary mapping slide templates to aspect ratios
templates_to_aspect_ratios = {
    "titleAndBody": "16:9",  # 1280x720
    "titleAndBullets": "4:3",  # 1024x768
    "twoColumn": "4:3",  # 800x600
    "sectionHeader": "16:9",  # 1280x720
    "blank": "16:9",  # 1280x720
}

GCS_BUCKET = "slide-images-bucket"

class ImageGenerator:
    def __init__(self, prompt_model=None, image_model=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        slide_prompt_path = os.path.join(script_dir, "prompt/slide_image_prompt.txt")
        with open(slide_prompt_path, 'r') as f:
            default_image_prompt = f.read()
        
        default_config = {
            "prompt_model": GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7),
            "prompt_model_prompt": default_image_prompt,
            "image_model": "flux",
        }

        self.prompt_model = prompt_model or default_config["prompt_model"]
        self.image_model = image_model or default_config["image_model"]
        self.prompt_model_prompt = default_config["prompt_model_prompt"]

    def _construct_image_generation_prompt(self, title: str, content: Union[str, list, dict], layout: str) -> str:
        """
        Constructs a detailed prompt for image generation based on slide content.
        Uses the slide_image_prompt.txt template and Google Gemini model to generate
        a high-quality image prompt.
        
        Args:
            title (str): The slide title
            content (str/list/dict): The slide content (can be various formats)
            layout (str): The slide layout/template
            
        Returns:
            str: A structured prompt for image generation
        """
        # Process content based on its type
        content_text = ""
        if isinstance(content, str):
            content_text = content
        elif isinstance(content, list):
            content_text = ". ".join(content)
        elif isinstance(content, dict):
            if "leftColumn" in content and "rightColumn" in content:
                content_text = f"{content['leftColumn']}. {content['rightColumn']}"
        
        prompt = PromptTemplate(
            template=self.prompt_model_prompt,
            input_variables=["title", "content"]
        )
        
        # Generate the image prompt using Gemini
        try:
            image_prompt_output = self.prompt_model.invoke(prompt.format(
                title=title,
                content=content_text
            ))

            return image_prompt_output
            
        except Exception as e:
            raise Exception(f"Error generating image prompt with Gemini: {str(e)}")

    def generate_slide_image(self, slide_id: int, title: str, content: Union[str, list, dict], layout: str) -> str:
        """
        Generates an image for a presentation slide and returns the URL.
        
        Args:
            slide_id (int): The slide ID
            title (str): The slide title
            content (str/list/dict): The slide content
            layout (str): The slide layout/template
            
        Returns:
            str: Public URL to the generated image on Google Cloud Storage
        """    
        try:
            # Get aspect ratio based on template
            aspect_ratio = templates_to_aspect_ratios.get(layout, "16:9")
            
            # Construct the prompt
            prompt = self._construct_image_generation_prompt(title, content, layout)
            logger.info(f"Generated image prompt: {prompt}...")
            
            # Call image generation API (Replicate's Flux model)
            input_params = {
                "prompt": prompt,
                "guidance": 7.5,
                "aspect_ratio": aspect_ratio
            }
            
            # Generate a unique filename
            filename = f"{slide_id}-{uuid.uuid4()}.png"
            
            logger.info(f"Calling image generation API for {self.image_model} model with aspect ratio: {aspect_ratio}")
            if self.image_model == "flux":
                start_time = time.time()
                output = replicate.run(
                    "black-forest-labs/flux-dev",
                    input=input_params
                )
                end_time = time.time()
                logger.info(f"Flux image generation took {end_time - start_time} seconds")

                output = output[0]
                # Read the FileOutput into a BytesIO object
                bio = BytesIO(output.read())
            # Imagen
            else:
                # project_id = os.getenv("GCP_PROJECT_ID")
                # vertexai.init(project=project_id, location=location)

                imagen_output_dir = "imagen_output"
                if not os.path.exists(imagen_output_dir):
                    os.makedirs(imagen_output_dir)

                model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")

                start_time = time.time()
                images = model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                    add_watermark=False,
                )
                end_time = time.time()
                logger.info(f"Imagen image generation took {end_time - start_time} seconds")

                bio = BytesIO()
                # Use the underlying PIL image object and save it with an explicit format
                images[0]._pil_image.save(bio, format="PNG")

            # Reset buffer position
            bio.seek(0)

            # Upload to GCS
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(filename)
            blob.upload_from_file(bio, content_type="image/png")
            blob.make_public()

            public_url = blob.public_url
            logger.info(f"Generated image was uploaded to {filename} in Google Cloud Storage. URL: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error generating slide image: {str(e)}")
            # Return a placeholder image if generation fails
            return f"https://via.placeholder.com/800x450.png?text={title.replace(' ', '+')}"
