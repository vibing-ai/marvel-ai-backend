from pydantic import BaseModel, Field
from typing import List, Optional
import os
from app.services.logger import setup_logger
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from app.services.schemas import PresentationGeneratorArgs
from fastapi import HTTPException

logger = setup_logger(__name__)

class OutlineGenerator:
    def __init__(self, args: PresentationGeneratorArgs, verbose=False):
        # Initialize LLM and parser for outline generation
        self.args = args
        self.verbose = verbose
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.parser = JsonOutputParser(pydantic_object=OutlineSchema)
        
    def compile(self) -> dict:
        try:
            # Create prompt for outline generation with learning objectives and structure
            prompt = PromptTemplate(
                template=(
                    "Generate a coherent presentation outline for grade {grade_level} students.\n\n"
                    "Topic: {topic}\n"
                    "Number of slides needed: {n_slides}\n"
                    "Learning objectives: {objectives}\n"
                    "Language: {lang}\n\n"
                    "Create an outline where:\n"
                    "1. Each slide has a clear topic\n"
                    "2. Include a brief description of the content\n"
                    "3. Add transitions between slides for smooth flow\n"
                    "4. Ensure content builds progressively\n"
                    "5. Match the grade level's comprehension\n"
                    "6. Generate exactly {n_slides} slides\n\n"
                    "{format_instructions}"
                ),
                input_variables=["grade_level", "topic", "n_slides", "objectives", "lang"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )

            chain = prompt | self.model | self.parser
            
            result = chain.invoke({
                "grade_level": self.args.grade_level,
                "topic": self.args.topic,
                "n_slides": self.args.n_slides,
                "objectives": self.args.objectives,
                "lang": self.args.lang
            })

            if self.verbose:
                logger.info(f"Generated outline successfully")

            return dict(result)

        except Exception as e:
            logger.error(f"Failed to generate outline: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate outline: {str(e)}")

# Defines expected structure for each slide in the outline
class OutlineSlide(BaseModel):
    topic: str = Field(description="The main topic or title of the slide")
    description: str = Field(description="Brief description of the slide content")
    transition: str = Field(description="How this slide connects to the next one for smooth flow")

class OutlineSchema(BaseModel):
    slides: List[OutlineSlide] = Field(description="List of slides with their topics and descriptions")