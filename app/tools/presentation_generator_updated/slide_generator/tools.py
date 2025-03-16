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
from app.services.schemas import SlideImageRequest
from app.tools.utils.tool_utilities import generate_slide_image, templates_to_aspect_ratios
from app.api.router import generate_slide_image

logger = setup_logger(__name__)

class SlideGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, slide_prompt=None, image_prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        # Read prompt files
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Read the prompt files
        slide_prompt_path = os.path.join(script_dir, "prompt/slide_generator_prompt.txt")
        image_prompt_path = os.path.join(script_dir, "prompt/slide_image_prompt.txt")
        
        with open(slide_prompt_path, 'r') as f:
            default_slide_prompt = f.read()
            
        with open(image_prompt_path, 'r') as f:
            default_image_prompt = f.read()
            
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=SlidePresentation),
            "slide_prompt": default_slide_prompt,
            "image_prompt": default_image_prompt,
            "vectorstore_class": Chroma
        }

        self.slide_prompt = slide_prompt or default_config["slide_prompt"]
        self.image_prompt = image_prompt or default_config["image_prompt"]
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
            template=self.slide_prompt,
            input_variables=["instructional_level", "topic", "slides_titles"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        chain = prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain

    def generate_slides(self):
        """Generate slides based on the provided outline."""
        
        slides_titles = self.args.slides_titles
        instructional_level = self.args.instructional_level
        topic = self.args.topic
        lang = self.args.lang or "en"

        logger.info(f"Generating slides for the presentation on topic: {topic}, level: {instructional_level}")
        logger.info(f"Slide titles: {slides_titles}")

        # Prepare the prompt template
        prompt = PromptTemplate(
            template=self.slide_prompt,
            input_variables=["slides_titles", "instructional_level", "topic", "lang"]
        )

        # Set up the chain
        chain = prompt | self.model | self.parser

        # Invoke the chain with the input parameters
        input_parameters = {
            "slides_titles": slides_titles,
            "instructional_level": instructional_level,
            "topic": topic,
            "lang": lang
        }
        logger.info(f"Input parameters: {input_parameters}")

        # Generate the slides content
        response = chain.invoke(input_parameters)
        logger.info(f"Generated slides: {response}")

        # Validate the content
        self.validate_slides_content(response, topic)

        # Loop through slides and generate images for each
        logger.info(f"Generating images for slides")
        for slide in response.slides:
            try:
                # Generate image for the slide
                image_url = generate_slide_image(
                    title=slide.title,
                    content=slide.content,
                    layout=slide.template
                )
                
                # Assign the image URL to the slide
                slide.image_url = image_url
                logger.info(f"Generated image for slide: {slide.title}")
            except Exception as e:
                logger.error(f"Error generating image for slide '{slide.title}': {str(e)}")
                # Provide a fallback image URL
                slide.image_url = f"https://via.placeholder.com/800x450.png?text={slide.title.replace(' ', '+')}"

        # Format the response
        formatted_response = {"data": {"slides": response.slides}}
        return formatted_response
        

class Slide(BaseModel):
    title: str = Field(..., description="The title of the slide")
    template: str = Field(..., description="The slide template type: sectionHeader, titleAndBody, titleAndBullets, twoColumn")
    content: str | list | dict | Any = Field(None, description="Content of the slide, can be string, list, dict, or any type")
    image_url: Optional[str] = Field(None, description="URL of the image for the slide (if applicable)")

class SlidePresentation(BaseModel):
    slides: List[Slide] = Field(..., description="The complete set of slides in the presentation")