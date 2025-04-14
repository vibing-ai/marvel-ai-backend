from langchain_core.messages import AIMessage, HumanMessage
#from langchain_google_vertexai.vision_models import VertexAIImageGeneratorChat, ImageGenerationModel
from vertexai.preview.vision_models import ImageGenerationModel
from PIL import Image
from app.services.logger import setup_logger
from typing import Literal, Optional
import io
logger = setup_logger(__name__)
class ImageGenerator:
    def __init__(self):
        self.generator  = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        self.prompts = []

    def generate_image(self, slide, slide_data):
        logger.info(f'Generating image for slide {slide} with prompt')
        model = self.generator
             
        prompt = f'Generate an image with {slide_data["image_prompt"]}.'
        #aspect_ratio = '16:9" if slide_data["template"] in ["titleAndBody", "sectionHeader"] else "4:3"
        response = model.generate_images(
            prompt=prompt,
            # Optional:
            number_of_images=1,
            seed=0,
            aspect_ratio="16:9"if slide_data["template"] in ["titleAndBody", "sectionHeader"] else "4:3",
            add_watermark=False,
        )
       # response= {"images": [None]}

        if response.images:
            generated_image = response.images[0]
            logger.info(f"Generated image for slide {slide}")
            logger.info(f"generated parameters: {generated_image._generation_parameters}")

            
           # Get image dimensions
            try:
                # Convert to PIL Image first
                image_bytes = generated_image._image_bytes
                pil_image = Image.open(io.BytesIO(image_bytes))
                width, height = pil_image.size
                logger.info(f'Generated image resolution: {width}x{height} for slide template {slide_data["template"]}')
            except Exception as e:
                logger.error(f"Failed to get image dimensions: {e}")
                width, height = None, None
            return generated_image
     
        else:
            logger.error("No images were generated.")
        return None


       