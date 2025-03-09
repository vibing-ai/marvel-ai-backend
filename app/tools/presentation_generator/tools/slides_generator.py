from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.services.logger import setup_logger
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from fastapi import HTTPException

logger = setup_logger(__name__)

class SlidesGenerator:
    def __init__(self, outline: dict, inputs: dict, verbose=False):
        # Initialize LLM and parser for detailed slide content generation
        self.outline = outline
        self.inputs = inputs
        self.verbose = verbose
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.parser = JsonOutputParser(pydantic_object=SlideContent)
        
    def compile(self) -> dict:
        try:
            # Create base context from input args
            base_context = (
                "Creating a presentation for:\n"
                f"Grade Level: {self.inputs['grade_level']}\n"
                f"Topic: {self.inputs['topic']}\n"
                f"Learning Objectives: {self.inputs['objectives']}\n"
                f"Language: {self.inputs['lang']}\n\n"
            )

            prompts = {}
            for idx, slide in enumerate(self.outline["slides"]):
                prompt = PromptTemplate(
                    template=(
                        f"{base_context}\n"
                        f"Generate content for Slide {idx + 1}:\n"
                        f"Topic: {slide['topic']}\n"
                        f"Description: {slide['description']}\n"
                        f"Transition: {slide['transition']}\n\n"
                        "Create engaging slide content that:\n"
                        "1. Is appropriate for the grade level\n"
                        "2. Uses clear and concise language\n"
                        "3. Includes key points and examples\n"
                        "4. Creates an appropriate segue as per the transition\n"
                        "5. Supports learning objectives\n\n"
                        "Return a JSON object with 'topic' and 'content' fields.\n"
                        "The 'content' field can contain any structured data you want.\n"
                        "Ensure the JSON is valid and complete.\n\n"
                        "{format_instructions}"
                    ),
                    input_variables=[],
                    partial_variables={"format_instructions": self.parser.get_format_instructions()}
                )
                prompts[f"slide_{idx + 1}"] = prompt

            chains = {
                key: prompt | self.model | self.parser
                for key, prompt in prompts.items()
            }

            parallel_pipeline = RunnableParallel(branches=chains)
            
            results = parallel_pipeline.invoke({})

            if self.verbose:
                logger.info(f"Generated {len(results['branches'])} slides successfully")

            # Compile final presentation structure
            presentation = PresentationSchema(
                slides=[results["branches"][f"slide_{i+1}"] for i in range(len(self.outline["slides"]))]
            )

            return dict(presentation)

        except Exception as e:
            logger.error(f"Failed to generate slides: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate slides: {str(e)}")

# Defines expected structure for each slide in the presentation
class SlideContent(BaseModel):
    topic: str = Field(description="The topic or title of the slide")
    content: Dict[str, Any] = Field(
        description="Structured content of the slide",
        example={
            "main_points": ["point 1", "point 2"],
            "examples": ["example 1", "example 2"],
            "details": "Additional explanation",
            "visual_notes": "Suggested visuals"
        }
    )
    # Example of a slide content
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Vectors and Vector Operations",
                "content": {
                    "main_points": [
                        "Definition of vectors",
                        "Vector addition and multiplication",
                        "Geometric interpretation"
                    ],
                    "examples": [
                        "Feature vectors in ML",
                        "Velocity vectors in physics"
                    ],
                    "details": "A vector is an ordered list of numbers...",
                    "visual_notes": "Draw 2D vector addition diagram"
                }
            }
        }

# Defines expected structure for the entire presentation
class PresentationSchema(BaseModel):
    slides: List[SlideContent] = Field(description="List of slides with their content")