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
from app.tools.presentation_generator_updated.image_generator.tools import ImageGenerator

logger = setup_logger(__name__)
        
class SlideGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, image_model=None, parser=None, verbose=False):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        slide_prompt_path = os.path.join(script_dir, "prompt/slide_generator_prompt.txt")
        with open(slide_prompt_path, 'r') as f:
            default_slide_prompt = f.read()
        slide_image_determination_prompt_path = os.path.join(script_dir, "prompt/slide_image_determination_prompt.txt")
        with open(slide_image_determination_prompt_path, 'r') as f:
            slide_image_determination_prompt = f.read()

        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=SlidePresentation),
            "prompt": default_slide_prompt,
            "vectorstore_class": Chroma,
            "image_model": "flux"
        }

        self.prompt = prompt or default_config["prompt"]
        self.slide_image_determination_prompt = slide_image_determination_prompt
        self.image_generator = ImageGenerator(image_model=image_model or default_config["image_model"])
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        self.image_model = image_model or default_config["image_model"]

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
        generate_prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["instructional_level", "topic", "slides_titles"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        generate_chain = generate_prompt | self.model | self.parser

        image_determination_prompt = PromptTemplate(
            template=self.slide_image_determination_prompt,
            input_variables=["slide_content"]
        )
        image_determination_chain = image_determination_prompt | GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)

        logger.info(f"Chain compilations complete")

        return (generate_chain, image_determination_chain)

    def generate_slides(self):
        logger.info(f"Creating the Outlines for the Presentation") 
        generate_chain, image_determination_chain = self.compile_context() 

        input_parameters = {
            "instructional_level": self.args.instructional_level,
            "topic": self.args.topic,
            "slides_titles": self.args.slides_titles,
            "lang": self.args.lang
        }

        response = generate_chain.invoke(input_parameters)

        logger.info(f"Generated slides!")
        # Add validation metrics
        validation_results = self.validate_slides_content(response=response, topic=self.args.topic)
        logger.info(f"Response validation: {validation_results}")
        
        if not validation_results["valid"]:
            logger.warning(f"Generated content may not fully match the requested topic")
        
        # Loop through slides and generate images for each one needing a slide
        logger.info(f"Generating images for slides...")
        new_slides = []
        i = 1
        for slide in response['slides']:
            # Does the slide need an image?
            slide_content = slide['content']
            image_determination = image_determination_chain.invoke({
                "slide_content": slide_content
            })
            if image_determination.strip().lower() == "yes":
                slide['needs_image'] = True
            
                # Generate image for the slide
                image_url = self.image_generator.generate_slide_image(
                    slide_id=i,
                    title=slide['title'],
                    content=slide_content,
                    layout=slide['template'],
                )
                
                # Assign the image URL to the slide
                slide['image_url'] = image_url
                logger.info(f"Generated image for slide: {slide['title']}")
            else:
                slide['needs_image'] = False
            
            new_slides.append(slide)
            i += 1

        # Format the response
        formatted_response = {"slides": new_slides}
        return formatted_response

class Slide(BaseModel):
    title: str = Field(..., description="The title of the slide")
    template: str = Field(..., description="The slide template type: sectionHeader, titleAndBody, titleAndBullets, twoColumn")
    content: str | list | dict | Any = Field(None, description="Content of the slide, can be string, list, dict, or any type")
    needs_image: bool = Field(None, description="Whether the slide needs an image")
    image_url: Optional[str] = Field(None, description="URL of the image for the slide (if applicable)")

class SlidePresentation(BaseModel):
    slides: List[Slide] = Field(..., description="The complete set of slides in the presentation")