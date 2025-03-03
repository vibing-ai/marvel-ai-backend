
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.schemas import OutlineGeneratorArgs
from app.services.logger import setup_logger
from langchain_core.prompts import PromptTemplate
import os

import json

logger = setup_logger()

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()

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
            # prompt = self._build_prompt(context, doc_content)

            promp = PromptTemplate(
                template=read_text_file("/prompt/outline_generator.txt"),
                input_variables=["leve", "context", "num_slides",],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )
            
            # Generate the outline using the AI model
            response = self.llm.invoke(prompt)
            
            if self.verbose:
                logger.info("AI model response received")
            
            # Extract and process the slide titles
            # slide_titles = self._process_response(response.content)
            
            return OutlineOutput(slides=slide_titles)
            
        except Exception as e:
            logger.error(f"Error in outline generation: {str(e)}")
            raise ValueError(f"Failed to generate outline: {str(e)}")
    
    # def _build_prompt(self, context, doc_content):
    #     """Build the prompt for the AI model."""
    
    #     return prompt
    
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
            try:
                slide_titles = json.loads(cleaned_text)
                
                # Check for generic slide titles
                generic_title_count = sum(1 for title in slide_titles if title.lower().startswith("slide "))
                if generic_title_count > 0:
                    logger.warning(f"Detected {generic_title_count} generic slide titles. Attempting to regenerate.")
                    # Try a simple fix - call the AI again with a stronger instruction
                    retry_prompt = f"""
                    You are an educational content specialist. The slide titles you provided are too generic.
                    
                    Create {self.args.num_slides} SPECIFIC and DESCRIPTIVE slide titles for a presentation on "{self.args.context}" for {self.args.level} level education.
                    
                    Each title must clearly indicate the content and be related to the topic. Do NOT use generic titles like "Slide 1".
                    
                    Return only a JSON array of slide titles.
                    """
                    retry_response = self.llm.invoke(retry_prompt)
                    cleaned_retry = retry_response.content.strip()
                    if cleaned_retry.startswith("```") and cleaned_retry.endswith("```"):
                        cleaned_retry = cleaned_retry[3:-3].strip()
                    if cleaned_retry.startswith("```json"):
                        cleaned_retry = cleaned_retry[7:].strip()
                        if cleaned_retry.endswith("```"):
                            cleaned_retry = cleaned_retry[:-3].strip()
                    
                    try:
                        new_titles = json.loads(cleaned_retry)
                        # Check if the new titles are better
                        new_generic_count = sum(1 for title in new_titles if title.lower().startswith("slide "))
                        if new_generic_count < generic_title_count:
                            slide_titles = new_titles
                    except:
                        logger.warning("Failed to parse retry response, keeping original titles")
                
                # Ensure we have the correct number of slides
                if len(slide_titles) != self.args.num_slides:
                    logger.warning(f"Expected {self.args.num_slides} slides but got {len(slide_titles)}")
                    # Adjust the number of slides if necessary
                    if len(slide_titles) > self.args.num_slides:
                        slide_titles = slide_titles[:self.args.num_slides]
                    else:
                        # If we have too few slides, generate specific slide titles based on context
                        topic_words = self.args.context.split()
                        missing_count = self.args.num_slides - len(slide_titles)
                        additional_slides = [f"{topic_words[0]} Subtopic {i+1}: Additional Content" for i in range(missing_count)]
                        slide_titles.extend(additional_slides)
                
                # Final check to replace any remaining generic titles
                for i, title in enumerate(slide_titles):
                    if title.lower().startswith("slide "):
                        topic_words = self.args.context.split()
                        if i == 0:
                            slide_titles[i] = f"Introduction to {self.args.context}"
                        elif i == len(slide_titles) - 1:
                            slide_titles[i] = f"Conclusion: Key Takeaways on {self.args.context}"
                        else:
                            slide_titles[i] = f"Key Aspect {i} of {self.args.context}"
                
                return slide_titles
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                # Create context-specific fallback titles rather than generic ones
                topic = self.args.context
                
                default_titles = [
                    f"Introduction to {topic}",
                    f"Background of {topic}",
                    f"Key Concepts in {topic}",
                    f"Important Components of {topic}"
                ]
                
                # Add more specific titles based on number needed
                remaining = self.args.num_slides - len(default_titles)
                if remaining > 0:
                    default_titles.extend([f"Aspect {i+1} of {topic}" for i in range(remaining-1)])
                    default_titles.append(f"Conclusion: Summary of {topic}")
                
                # Trim if we have too many
                return default_titles[:self.args.num_slides]
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            # Return a default set of slide titles
            return [f"Slide {i+1}" for i in range(self.args.num_slides)]
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return [f"Slide {i+1}" for i in range(self.args.num_slides)]

class OutlineSlideItem(BaseModel):
    """Represents a single slide title in the outline."""
    title: str

class OutlineOutput(BaseModel):
    """Output model for the outline generator."""
    slides: List[str] = Field(..., description="List of slide titles in the outline")
