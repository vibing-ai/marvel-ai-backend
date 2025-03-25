from pydantic import BaseModel, Field
from typing import List, Optional,Union, Any
import os
from app.services.logger import setup_logger
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from app.tools.presentation_generator_updated.slide_generator.imagen import ImageGenerator
from app.tools.presentation_generator_updated.slide_generator.firebase import FirebaseManager
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
            "prompt_with_context": read_text_file("prompt/slide_generator_prompt_with_context.txt"),
    
            "vectorstore_class": Chroma
        }
        self.prompt_with_context= default_config["prompt_with_context"] 
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose
        self.context =None
        self.image_generator=ImageGenerator()
        self.firebase = FirebaseManager()
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

    def compile_with_context(self, documents: List[Document]):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["instructional_level", "topic","context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        if self.runner is None:
            logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            logger.info(f"Vectorstore created") if self.verbose else None

            retriever = self.vectorstore.as_retriever()
            logger.info(f"Retriever created successfully") if self.verbose else None
            
            query = f"Retrieve all relevant information for the following topics: {', '.join(self.args.slides_titles)}. Provide key explanations, concepts, and insights for each topic."
            context_documents = retriever.invoke(query)
            def extract_content(documents):
                return [doc.page_content for doc in documents]
            self.context = extract_content(context_documents)
            logger.info(f"Retrieved context") if self.verbose else None 
                 
            
        chain = prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain
 
        

    def compile_context(self):        
        #Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["instructional_level", "topic", "slides_titles"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        chain = prompt | self.model | self.parser
        logger.info(f"Chain compilation complete")
        return chain    

    
    def generate_slide_image(self, slide_key, slide_data):
         """
        Create a RunnableLambda for processing a single slide image
        """
         
         def process_image_for_slide(_):
                if not slide_data.get("needs_image", False) or not slide_data.get("image_prompt"):
                    return None
                logger.info(f"Generating image for slide {slide_key}")
            
                image_data = self.image_generator.generate_image(
                    slide_key, 
                    slide_data
                )
                
                # Upload the image to Firebase
                image_url = self.firebase.upload_image(
                    image_data, 
                    f"slides/{self.args.topic.replace(' ', '_')}/slide_{slide_key}.png"
                )
                logger.info(f"Image URL: {image_url} {self.args.topic.replace(' ', '_')}/{slide_key}.png")
                logger.info(f"Image uploaded to Firebase for slide {slide_key}")                 
                # Return the image URL to be added to the slide data
                return {"slide_key": slide_key, "image_url": image_url}
        
         return RunnableLambda(process_image_for_slide)

    def generate_slides(self, documents: Optional[List[Document]]):
        logger.info(f"Generating slides for the Presentation")

        if(documents):
            chain = self.compile_with_context(documents)
        else:
            chain = self.compile_context() 
        
        input_parameters = {
            "instructional_level": self.args.instructional_level,
            "topic": self.args.topic,
            "slides_titles": self.args.slides_titles,
            "context":self.context,
            "lang": self.args.lang
        }
    
        logger.info(f"Input parameters: {input_parameters}")

        response = chain.invoke(input_parameters)
        logger.info(f"Generated response: {response}")
        

        TEMPLATE_CONFIGS = {
            'titleAndBody': (1280, 720),
            'titleAndBullets': ( 1024, 768),
            'twoColumn': ( 800, 600),
            'sectionHeader':(1600, 900)
        }
        # Default configuration for unknown templates
        DEFAULT_TEMPLATE = ( 0, 0)

        for slide in response["slides"]:
           width, height = TEMPLATE_CONFIGS.get(slide['template'], DEFAULT_TEMPLATE)
           slide['width'] = width
           slide['height'] = height

         # Add validation metrics
       # validation_results = self.validate_slides_content(response=response, topic=self.args.topic)
      #  logger.info(f"Response validation: {validation_results}")
        
      #  if not validation_results["valid"]:
      #      logger.warning(f"Generated content may not fully match the requested topic")
        
        image_chains = {}
        
        for index, slide in enumerate(response["slides"]):
            if slide['needs_image']:       
                image_chains[f"image_{index}"] = self.generate_slide_image(index, slide)
        logger.info(f"Image chains created,{image_chains}")

         # Only run image generation if there are images to generate
        if image_chains:
            #only run first 2 slides due to quota limits
            image_chains_with2URLS = {k: v for i, (k, v) in enumerate(image_chains.items()) if i < 2}
            image_pipeline = RunnableParallel(image_chains_with2URLS)
            #image_pipeline = RunnableParallel(image_chains)
            image_results = image_pipeline.invoke({})

        logger.info(f"Image generation complete {image_results}")

        #  Add image URLs to the slide results
        for result in image_results.values():
                slide_index = result["slide_key"]
                response["slides"][slide_index]["image_url"] = result["image_url"]

        logger.info(f"Image URLs added to slide results ")
       
         # Transform response to only include required fields
        simplified_slides = [
        SlideOutput(
            title=slide["title"],
            template=slide["template"],
            content=slide["content"],
            image_url=slide.get("image_url", None)  # Use get() to handle cases where image_url might not exist
        ) for slide in response["slides"]
    ]
        logger.info(f"Presentation generated successfully: {simplified_slides}")
        
        return simplified_slides

class Slide(BaseModel):
    title: str = Field(..., description="The title of the slide")
    template: str = Field(..., description="The slide template type: sectionHeader, titleAndBody, titleAndBullets, twoColumn")
    content: str | list | dict | Any = Field(None, description="Content of the slide, can be string, list, dict, or any type")
    needs_image: bool = Field(..., description="Whether an image is needed for the slide")
    image_prompt: str = Field(..., description="The visual notes of the slide")
    style: str = Field(..., description="The style of the slide")
   

class SlidePresentation(BaseModel):
    slides: List[Slide] = Field(..., description="The complete set of slides in the presentation")
 
class SlideOutput(BaseModel):
    title: str = Field(..., description="The title of the slide")
    template: str = Field(..., description="The slide template type: sectionHeader, titleAndBody, titleAndBullets, twoColumn")
    content: str | list | dict | Any = Field(None, description="Content of the slide, can be string, list, dict, or any type")
    image_url: str | None = Field (default=None,description="The URL of the generated image for the slide")
