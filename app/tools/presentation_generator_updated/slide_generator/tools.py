from pydantic import BaseModel, Field
from typing import List, Optional,Union, Any
import os
from app.services.logger import setup_logger
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
# from app.tools.presentation_generator_updated.slide_generator.image_generator import ImageGenerator, image_generation_pipeline
from app.tools.presentation_generator_updated.image_generator.core import executor as image_executor
import re
logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()
    
class SlideGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=SlidePresentation),
            "prompt": read_text_file("prompt/slide_generator_prompt.txt"),
            "vectorstore_class": Chroma
        }

        self.prompt = prompt or default_config["prompt"]
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
        # logger.info(f"Input parameters: {input_parameters}")
        
        # Generate slide content using the chain
        response = chain.invoke(input_parameters)
        logger.info(f"Response type: {type(response)}")

        # logger.info(f"Generated response: {response}")

        # Generate images
        image_URLs = image_executor(response, self.args.lang)
        final_slides = self.attach_image_URLs(response, image_URLs)
        logger.info(f"Final Slides type: {image_URLs}")

        # logger.info(f"Generated response with images: {response}")
        
        validation_results = self.validate_slides_content(response=final_slides, topic=self.args.topic)
        # logger.info(f"Response validation: {validation_results}")
        
        if not validation_results["valid"]:
            logger.warning(f"Generated content may not fully match the requested topic")
        return final_slides
    
    def attach_image_URLs(self, response, image_URLs):
        try:
            if not response or not isinstance(response, dict) or "slides" not in response:
                raise ValueError("Invalid response format")
            
            for slide in response["slides"]:
                try:
                    if "title" not in slide:
                        raise KeyError("Slide missing title")
                    
                    slide["image_URL"] = image_URLs['data'][slide["title"]]
                    if not slide["image_URL"]:
                        logger.warning(f"No image URL found for slide: {slide['title']}")
                        
                except KeyError as ke:
                    logger.error(f"Error processing slide: {ke}")
                    slide["image_URL"] = None
                    
            return response
            
        except Exception as e:
            logger.error(f"Error attaching image URLs: {str(e)}")
            raise ValueError(f"Failed to attach image URLs: {str(e)}")
    
    def mock_image_executor(self, response, lang):
        return {
            'Introduction to Linear Algebra: What is it and why does it matter?': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/Introduction%20to%20Linear%20Algebra%20What%20is%20it%20and%20why%20does%20it%20matter_20250328_110744.png',
            'What is Linear Algebra?': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/What%20is%20Linear%20Algebra_20250328_110746.png',
            'Why is Linear Algebra Important?': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/Why%20is%20Linear%20Algebra%20Important_20250328_110744.png',
            'Linear Algebra in Action: Real-World Examples': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/Linear%20Algebra%20in%20Action%20Real-World%20Examples_20250328_110746.png',
            'Linear Equations vs. Linear Transformations': 'https://storage.googleapis.com/marvel_ai_backend_bucket/presentation_images/Linear%20Equations%20vs%20Linear%20Transformations_20250328_110748.png'
        }

class Slide(BaseModel):
    title: str = Field(..., description="The title of the slide")
    template: str = Field(..., description="The slide template type: sectionHeader, titleAndBody, titleAndBullets, twoColumn")
    #content: Optional[Union[str, list, dict, Any]] = Field(None, description="Content of the slide, can be string, list, dict, or any type")
    content: str | list | dict | Any = Field(None, description="Content of the slide, can be string, list, dict, or any type")

class SlidePresentation(BaseModel):
    slides: List[Slide] = Field(..., description="The complete set of slides in the presentation")
