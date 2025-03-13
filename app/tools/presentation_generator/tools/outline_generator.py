from pydantic import BaseModel, Field
from typing import List, Optional
import os
from app.services.logger import setup_logger
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from google.cloud import vertexai
import vertexai.language_models as lm
from fastapi import HTTPException
from app.services.schemas import PresentationGeneratorArgs  # Updated schema

logger = setup_logger(__name__)

class OutlineSlide(BaseModel):
    topic: str = Field(description="The main topic or title of the slide")
    description: str = Field(description="Brief description of the slide content")
    transition: str = Field(description="How this slide connects to the next one for smooth flow")

class OutlineSchema(BaseModel):
    slides: List[OutlineSlide] = Field(description="List of slides with their topics and descriptions")

class OutlineGenerator:
    def __init__(self, args: PresentationGeneratorArgs, verbose=False):
        vertexai.init(project="marvelai-project", location="us-central1")
        self.model = lm.TextGenerationModel.from_pretrained("gemini-1.5-pro")
        self.parser = JsonOutputParser(pydantic_object=OutlineSchema)
        self.args = args
        self.verbose = verbose

        # Validate required inputs (aligned with PRD)
        if not self.args.text: raise ValueError("Topic must be provided")
        if not self.args.slideCount: raise ValueError("Number of slides must be provided")
        if int(self.args.slideCount) < 5 or int(self.args.slideCount) > 20:
            raise ValueError("Number of slides must be between 5 and 20")
        if not self.args.instructionalLevel: raise ValueError("Instructional level must be provided")

    def compile(self) -> dict:
        try:
            prompt = PromptTemplate(
                template=(
                    "Generate a coherent presentation outline for {instructionalLevel} students.\n\n"
                    "Topic: {text}\n"
                    "Number of slides needed: {slideCount}\n"
                    "Learning objectives: {objectives}\n"
                    "Additional comments: {additional_comments}\n\n"
                    "Create an outline where:\n"
                    "1. Each slide has a clear topic\n"
                    "2. Include a brief description of the content\n"
                    "3. Add transitions between slides for smooth flow\n"
                    "4. Ensure content builds progressively\n"
                    "5. Match the instructional level's comprehension\n"
                    "6. Generate exactly {slideCount} slides\n\n"
                    "{format_instructions}"
                ),
                input_variables=["instructionalLevel", "text", "slideCount", "objectives", "additional_comments"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )
            chain = prompt | self.model | self.parser
            result = chain.invoke({
                "instructionalLevel": self.args.instructionalLevel,
                "text": self.args.text,
                "slideCount": self.args.slideCount,
                "objectives": self.args.objectives or "",
                "additional_comments": self.args.additional_comments or ""
            })
            if self.verbose:
                logger.info("Generated outline successfully")
            return dict(result)  # Returns {"slides": [...]}
        except Exception as e:
            logger.error(f"Failed to generate outline: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate outline: {str(e)}")

def executor(instructionalLevel: str, slideCount: int, text: str, objectives: str = "", additional_comments: str = "", verbose: bool = False) -> dict:
    args = PresentationGeneratorArgs(
        instructionalLevel=instructionalLevel,
        slideCount=slideCount,
        text=text,
        objectives=objectives,
        additional_comments=additional_comments,
        objectives_file_url="",
        objectives_file_type="",
        additional_comments_file_url="",
        additional_comments_file_type=""
    )
    generator = OutlineGenerator(args, verbose)
    return generator.compile()