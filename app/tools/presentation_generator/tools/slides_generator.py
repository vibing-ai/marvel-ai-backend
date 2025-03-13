from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.services.logger import setup_logger
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from google.cloud import vertexai
import vertexai.language_models as lm
from fastapi import HTTPException

logger = setup_logger(__name__)

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
    speaker_notes: str = Field(  # New field added
        description="Detailed notes for the presenter to assist in delivering the slide content",
        example="Begin by introducing the topic, elaborate on the main points with examples, and smoothly transition to the next slide by previewing its focus."
    )
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
                },
                "speaker_notes": "Start with a simple definition of vectors, use the diagram to explain addition, and connect to real-world examples like ML and physics before moving to the next topic."
            }
        }

class PresentationSchema(BaseModel):
    slides: List[SlideContent] = Field(description="List of slides with their content and speaker notes")

class SlidesGenerator:
    def __init__(self, outline: dict, inputs: dict, verbose=False):
        vertexai.init(project="marvelai-project", location="us-central1")
        self.model = lm.TextGenerationModel.from_pretrained("gemini-1.5-pro")
        self.parser = JsonOutputParser(pydantic_object=SlideContent)
        self.outline = outline
        self.inputs = inputs
        self.verbose = verbose

    def compile(self) -> dict:
        try:
            base_context = (
                "Creating a presentation for:\n"
                f"Instructional Level: {self.inputs['instructionalLevel']}\n"
                f"Topic: {self.inputs['text']}\n"
                f"Learning Objectives: {self.inputs['objectives']}\n"
                f"Additional Comments: {self.inputs['additional_comments']}\n\n"
            )
            prompts = {}
            for idx, slide in enumerate(self.outline["slides"]):
                prompt = PromptTemplate(
                    template=(
                        f"{base_context}"
                        f"Generate content for Slide {idx + 1}:\n"
                        f"Topic: {slide['topic']}\n"
                        f"Description: {slide['description']}\n"
                        f"Transition: {slide['transition']}\n\n"
                        "Create engaging slide content that:\n"
                        "1. Is appropriate for the instructional level\n"
                        "2. Uses clear and concise language\n"
                        "3. Includes key points and examples\n"
                        "4. Creates an appropriate segue as per the transition\n"
                        "5. Supports learning objectives\n"
                        "6. Includes detailed speaker notes to assist the presenter in delivering the content\n\n"
                        "Return a JSON object with 'topic', 'content', and 'speaker_notes' fields.\n"
                        "- 'content' should contain structured data (e.g., main_points, examples, details, visual_notes).\n"
                        "- 'speaker_notes' should provide specific guidance for the presenter (e.g., what to say, how to explain).\n"
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
            parallel_pipeline = RunnableParallel(**chains)
            
            results = parallel_pipeline.invoke({})
            if self.verbose:
                logger.info(f"Generated {len(results)} slides with speaker notes successfully")

            presentation = PresentationSchema(
                slides=[results[f"slide_{i+1}"] for i in range(len(self.outline["slides"]))]
            )
            return dict(presentation)
        except Exception as e:
            logger.error(f"Failed to generate slides: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate slides: {str(e)}")

def executor(outline: Dict[str, List[Dict[str, str]]], instructionalLevel: str, text: str, objectives: str = "", additional_comments: str = "", verbose: bool = False) -> dict:
    inputs = {
        "instructionalLevel": instructionalLevel,
        "text": text,
        "objectives": objectives,
        "additional_comments": additional_comments
    }
    generator = SlidesGenerator(outline, inputs, verbose)
    return generator.compile()