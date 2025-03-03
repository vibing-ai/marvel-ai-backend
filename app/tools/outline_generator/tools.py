
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.logger import setup_logger
import json

logger = setup_logger()

class OutlineSlideItem(BaseModel):
    """Represents a single slide title in the outline."""
    title: str

class OutlineOutput(BaseModel):
    """Output model for the outline generator."""
    slides: List[str] = Field(..., description="List of slide titles in the outline")

# class OutlineGeneratorArgs(BaseModel):
#     """Input arguments for the outline generator."""
#     context: str = Field(..., description="The context or topic for the outline")
#     num_slides: int = Field(..., description="Number of slides to generate")
#     level: str = Field(..., description="Instructional level (Elementary, Middle School, High School, University)")
#     file_url: Optional[str] = Field(None, description="URL of a file with additional context")
#     file_type: Optional[str] = Field(None, description="Type of the file")
#     lang: Optional[str] = Field("en", description="Language for the outline")

class OutlineGenerator:
    """Class to generate slide outlines based on user inputs."""
    
    def __init__(self, args: OutlineGeneratorArgs, verbose: bool = False):
        """Initialize the outline generator with arguments and optional verbosity."""
        self.args = args
        self.verbose = verbose
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
        
    def create_outline(self, docs=None):
        """Generate a structured outline with the specified number of slides."""
        try:
            # Build the context from args and docs
            context = f"Topic: {self.args.context}\n"
            context += f"Educational Level: {self.args.level}\n"
            context += f"Number of Slides: {self.args.num_slides}\n"
            
            # Add document content if available
            doc_content = ""
            if docs:
                doc_content = "\n".join([doc.page_content for doc in docs])
                if self.verbose:
                    logger.info(f"Including additional content from documents")
            
            # Create the prompt for the AI model
            prompt = self._build_prompt(context, doc_content)
            
            # Generate the outline using the AI model
            response = self.llm.invoke(prompt)
            
            if self.verbose:
                logger.info("AI model response received")
            
            # Extract and process the slide titles
            slide_titles = self._process_response(response.content)
            
            return OutlineOutput(slides=slide_titles)
            
        except Exception as e:
            logger.error(f"Error in outline generation: {str(e)}")
            raise ValueError(f"Failed to generate outline: {str(e)}")
    
    def _build_prompt(self, context, doc_content):
        """Build the prompt for the AI model."""
        prompt = f"""
        You are an educational content specialist. Create an outline for a presentation with {self.args.num_slides} slides on the topic: "{self.args.context}" for {self.args.level} level education.

        {context}

        Additional context information:
        {doc_content if doc_content else "No additional context provided."}

        Output Requirements:
        1. Generate exactly {self.args.num_slides} slide titles.
        2. Ensure titles are clear, concise, and educational Make .
        3. Follow a logical flow from introduction to conclusion.
        4. Match the {self.args.level} educational level in complexity and depth.
        5. Format your response as a JSON array of strings ONLY (no explanation text).
        
        For example: ["Introduction to Topic", "First Main Point", "Second Main Point", "Applications", "Conclusion"]
        
        Return only the JSON array of slide titles.
        """
        return prompt
    
    def _process_response(self, response_text):
        """Process the AI response to extract the slide titles."""
        try:
            # Clean the response text to extract just the JSON array
            cleaned_text = response_text.strip()
            
            # Remove any markdown code block indicators if present
            if cleaned_text.startswith("```") and cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[3:-3].strip()
                
            # Remove any language indicators after the first ``` if present
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.split("\n", 1)[1].strip()
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3].strip()
            
            # Parse the JSON array
            slide_titles = json.loads(cleaned_text)
            
            # Ensure we have the correct number of slides
            if len(slide_titles) != self.args.num_slides:
                logger.warning(f"Expected {self.args.num_slides} slides but got {len(slide_titles)}")
                # Adjust the number of slides if necessary
                if len(slide_titles) > self.args.num_slides:
                    slide_titles = slide_titles[:self.args.num_slides]
                else:
                    # If we have too few slides, add generic ones to reach the target
                    additional_slides = [f"Additional Content {i+1}" for i in range(self.args.num_slides - len(slide_titles))]
                    slide_titles.extend(additional_slides)
            
            return slide_titles
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            # Return a default set of slide titles
            return [f"Slide {i+1}" for i in range(self.args.num_slides)]
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return [f"Slide {i+1}" for i in range(self.args.num_slides)]
