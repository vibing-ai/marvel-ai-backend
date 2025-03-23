from typing import List, Dict, Any
import asyncio
from google.cloud import aiplatform
from google.cloud import storage
import base64
from datetime import datetime
from app.services.logger import setup_logger
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
import uuid

logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

class SlideImageGenerator:
    def __init__(self, slides: List[dict], verbose: bool = False):
        self.slides = slides
        self.verbose = verbose
        
        try:
            project_id = os.getenv('PROJECT_ID')
            self.bucket_name = os.getenv('SLIDE_IMAGES_BUCKET_NAME')
            
            if not project_id:
                raise ValueError("PROJECT_ID environment variable is not set")
                
            # Initialize Vertex AI with project details
            vertexai.init(project=project_id)
            
            if self.verbose:
                logger.info(f"Initialized Vertex AI for project: {project_id}")
                logger.info(f"Using storage bucket: {self.bucket_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud services: {str(e)}")
            raise RuntimeError(f"Google Cloud initialization failed: {str(e)}")

    def needs_image(self, slide: dict) -> bool:
        """
        Determine if a slide needs an image based on both title and content.
        Handles different content formats and focuses on content purpose.
        """
        title = slide["title"].lower()
        content = slide["content"]
        
        # Convert content to analyzable text regardless of format
        content_text = ""
        if isinstance(content, str):
            content_text = content.lower()
        elif isinstance(content, dict):
            # Handle two-column format
            content_text = f"{content.get('leftColumn', '')} {content.get('rightColumn', '')}".lower()
        elif isinstance(content, list):
            # Handle bullet points
            content_text = " ".join(content).lower()
        
        # Non-visual content indicators: skips image generation 
        # if the slide title or content contains any of the following words
        # Skips transitions, summaries, conclusions, thank yous, questions, key takeaways, further exploration slides
        skip_indicators = [
            "summary", "conclusion", "thank you", "questions",
            "key takeaways", "further exploration", "transition", "transition slide"
        ]
        
        # Check both title and content for skip indicators
        if any(indicator in title for indicator in skip_indicators):
            if self.verbose:
                logger.info(f"Skipping image for slide: {slide['title']} - title indicates non-visual content")
            return False
        
        if any(indicator in content_text for indicator in skip_indicators):
            if self.verbose:
                logger.info(f"Skipping image for slide: {slide['title']} - content indicates non-visual content")
            return False
        
        # Generate for all other content-rich slides
        if self.verbose:
            logger.info(f"Generating image for slide: {slide['title']}")
        return True

    def generate_prompt(self, slide: dict) -> str:
        """Generate an image prompt using Gemini Pro with safety guardrails."""
        try:
            # Format content based on slide type
            content_text = ""
            if isinstance(slide["content"], str):
                content_text = slide["content"]
            elif isinstance(slide["content"], dict):
                content_text = f"""Left column: {slide["content"].get('leftColumn', '')}
                Right column: {slide["content"].get('rightColumn', '')}"""
            elif isinstance(slide["content"], list):
                content_text = "\n- " + "\n- ".join(slide["content"])

            prompt = PromptTemplate(
                template="""Create a visual prompt for an AI image generator (Imagen) that will generate a complementary image for presentation slide below.

                Important Guidelines:
                - Create conceptual visuals that support the content's meaning
                - Use representations, such as, geometric shapes, or symbolic imagery
                - AVOID requesting human faces, realistic human figures, or identifiable people
                - AVOID text, diagrams, charts, or mathematical symbols
                - Focus and latch onto a single clear concept from the slide content that can be visually represented.
                - Keep the style consistent with educational presentations
                - Keep the prompt concise and to the point (max 45 words)
                - For applications or examples, use metaphorical objects rather than human activities

                Presentation Slide Information:
                Title: {title}
                Content: {content}
                Template: {template}

                Generate only the image prompt without any explanations or additional text.""",
                input_variables=["title", "content", "template"]
            )

            llm = GoogleGenerativeAI(model="gemini-1.5-pro")
            
            response = llm.invoke(
                prompt.format(
                    title=slide["title"],
                    content=content_text,
                    template=slide["template"]
                )
            )
            
            generated_prompt = response.strip()
            
            if self.verbose:
                logger.info(f"Generated image prompt for slide: {slide['title']}")
                logger.debug(f"Image prompt: {generated_prompt}")

            return generated_prompt

        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            raise

    def generate_image(self, prompt: str) -> bytes:
        """Generate an image using Vertex AI."""
        try:
            # Initialize Vertex AI Imagen model
            image_model = ImageGenerationModel.from_pretrained("imagen-3.0-fast-generate-001")  # or latest version
            
            # Generate image
            response = image_model.generate_images(
                prompt=prompt,
                number_of_images=1,
            )           
            
            # Try to access the image bytes
            try:
                image_bytes = response[0]._image_bytes
                if self.verbose:
                    logger.info(f"Generated image with size {len(image_bytes)}")
                return image_bytes
            except Exception as e:
                logger.error(f"Failed to access image bytes: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            raise

    def store_image(self, image_data: bytes, slide_index: int) -> str:
        """Store the generated image and return its public URL."""
        try:
            # Initialize storage client
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)  # Use the bucket name from initialization
            
            # Generate unique filename using timestamp and UUID for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for brevity
            filename = f"slide_{slide_index}_{timestamp}_{unique_id}.png"
            
            # Create and upload blob
            blob = bucket.blob(filename)
            blob.upload_from_string(image_data, content_type="image/png")
            
            # Make the blob publicly accessible
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Image storage failed: {str(e)}")
            raise

    def process_slide(self, slide: dict, index: int) -> dict:
        """Process a single slide."""
        try:
            if not self.needs_image(slide):
                return {
                    "slide_number": index + 1,
                    "title": slide["title"],
                    "image_url": None,
                    "status": "skipped"
                }

            prompt = self.generate_prompt(slide)
            image_data = self.generate_image(prompt)
            image_url = self.store_image(image_data, index)
            
            return {
                "slide_number": index + 1,
                "title": slide["title"],
                "image_url": image_url,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing slide {index + 1}: {str(e)}")
            return {
                "slide_number": index + 1,
                "title": slide["title"],
                "image_url": None,
                "status": "error",
                "error": str(e)
            }

    def generate_slides(self) -> Dict[str, Any]:
        """Process all slides concurrently using threads."""
        try:
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(
                    lambda x: self.process_slide(x[1], x[0]), 
                    enumerate(self.slides)
                ))
            
            return {
                "status": "success",
                "slides": results
            }
            
        except Exception as e:
            logger.error(f"Error in generate_slides: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }