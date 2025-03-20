from pydantic import BaseModel, Field
from typing import List, Optional,Union, Any
import os
import re
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from app.services.logger import setup_logger
from app.tools.image_generator.tools import ImageGenerator

logger = setup_logger(__name__)
        
class SlideGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, image_model=None, parser=None, verbose=False):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        slide_prompt_path = os.path.join(script_dir, "prompt/slide_generator_prompt.txt")
        with open(slide_prompt_path, 'r') as f:
            default_slide_prompt = f.read()     

        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=SlidePresentation),
            "prompt": default_slide_prompt,
            "vectorstore_class": Chroma,
            "image_model": "flux"
        }

        self.prompt = prompt or default_config["prompt"]
        self.image_generator = ImageGenerator(image_model=image_model or default_config["image_model"])
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose

        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
       
    def validate_slides_content(self, response, topic):
        """Validates that slide content matches the requested topic and level."""
        topic_keywords = set(topic.lower().split())
        topic_coverage = 0
        garbage_coverage = 0
        template_requirements_met = False
        slides = response["slides"]
        try:
            if  len(slides) == 0:
                raise ValueError("No slides found in the response")
            for slide in slides:
                slide_text = ""
                if slide["template"] == "twoColumn":
                    template_requirements_met = True
                    
                if isinstance(slide["content"], list):
                    slide_text = ' '.join(slide["content"])
                elif isinstance(slide["content"], dict):
                    slide_text = ' '.join(slide["content"].values())
                else:
                    slide_text = slide["content"]
                # Check for topic keywords in the slide text
                if any(keyword in slide_text.lower() for keyword in topic_keywords):
                    topic_coverage += 1
            
            # Check for Markdown remnants or excessive newlines
                if any(char in slide_text for char in ['*', '\n', '`', '_']):
                    garbage_coverage += 1
        
            coverage_percentage = (topic_coverage / len(slides)) * 100
            garbage_coverage_percentage = (garbage_coverage / len(slides)) * 100
        
            return {
                "topic_coverage": coverage_percentage,
                "template_requirements_met": template_requirements_met,
                "garbage_coverage_percentage": garbage_coverage_percentage,
                "valid": coverage_percentage > 70 and template_requirements_met and garbage_coverage_percentage == 0
            }
            
        except ValueError as e:
            raise ValueError(e)


    def compile_context(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["instructional_level", "topic", "slides_titles"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        chain = prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain

    def generate_slides(self):
        logger.info(f"Creating the Outlines for the Presentation") 
        chain = self.compile_context() 

        input_parameters = {
            "instructional_level": self.args.instructional_level,
            "topic": self.args.topic,
            "slides_titles": self.args.slides_titles,
            "lang": self.args.lang
        }
        logger.info(f"Input parameters: {input_parameters}")

        response = chain.invoke(input_parameters)

        logger.info(f"Generated response: {response}")
         # Add validation metrics
        validation_results = self.validate_slides_content(response=response, topic=self.args.topic)
        logger.info(f"Response validation: {validation_results}")
        
        if not validation_results["valid"]:
            logger.warning(f"Generated content may not fully match the requested topic")
        
        # Loop through slides and generate images for each
        logger.info(f"Generating images for slides...")
        new_slides = []
        i = 1 # i is slide ID
        for slide in response['slides']:
            # Add a status field to track image generation status
            slide['image_generation_status'] = 'pending'
            
            max_retries = 1
            retry_count = 0
            success = False
            
            while retry_count <= max_retries and not success:
                try:
                    if retry_count > 0:
                        logger.info(f"Retrying image generation for slide: {slide['title']} (Attempt {retry_count + 1})")
                    
                    # Generate image for the slide
                    image_url = self.image_generator.generate_slide_image(
                        id=i,
                        title=slide['title'],
                        content=slide['content'],
                        layout=slide['template'],
                    )
                    
                    # Assign the image URL to the slide
                    slide['image_url'] = image_url
                    slide['image_generation_status'] = 'success'
                    logger.info(f"Generated image for slide: {slide['title']}")
                    success = True
                    
                except Exception as e:
                    retry_count += 1
                    error_message = str(e)
                    logger.warning(f"Image generation attempt {retry_count} failed for slide '{slide['title']}': {error_message}")
                    
                    # If we've exhausted all retries, set the placeholder and log the error
                    if retry_count > max_retries:
                        logger.error(f"All image generation attempts failed for slide '{slide['title']}': {error_message}")
                        # Provide a fallback image URL
                        slide['image_url'] = f"https://via.placeholder.com/800x450.png?text={slide['title'].replace(' ', '+')}"
                        slide['image_generation_status'] = 'failed'
                        slide['image_generation_error'] = error_message
            
            new_slides.append(slide)
            i += 1

        # Count failed images for user notification
        failed_images = sum(1 for slide in new_slides if slide['image_generation_status'] == 'failed')
        if failed_images > 0:
            logger.warning(f"{failed_images} out of {len(new_slides)} images failed to generate")
        
        # Format the response
        formatted_response = {
            "data": {
                "slides": new_slides,
                "metadata": {
                    "total_slides": len(new_slides),
                    "failed_images": failed_images,
                    "user_notification": f"Some slide images ({failed_images}) could not be generated and were replaced with placeholders." if failed_images > 0 else None
                }
            }
        }
        return formatted_response


class Slide(BaseModel):
    title: str = Field(..., description="The title of the slide")
    template: str = Field(..., description="The slide template type: sectionHeader, titleAndBody, titleAndBullets, twoColumn")
    content: str | list | dict | Any = Field(None, description="Content of the slide, can be string, list, dict, or any type")
    image_url: Optional[str] = Field(None, description="URL of the image for the slide (if applicable)")

class SlidePresentation(BaseModel):
    slides: List[Slide] = Field(..., description="The complete set of slides in the presentation")