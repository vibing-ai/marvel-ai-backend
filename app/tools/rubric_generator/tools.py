from pydantic import BaseModel, Field, validator, create_model
from typing import List, Dict, Optional, Type, Any
import os
import logging
import json
from enum import Enum
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.logger import setup_logger

# Define file types as an enum for better type safety
class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"
    CSV = "csv"
    YOUTUBE = "youtube"
    WEBSITE = "website"
    GSHEET = "gsheet"

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()
    
class RubricGeneratorArgs(BaseModel):
    """Arguments for the RubricGenerator."""
    grade_level: str = Field(
        ...,
        description="The grade level for the rubric (e.g., '9th Grade' or 'University')",
        min_length=1
    )
    point_scale: int = Field(
        ...,
        description="The number of performance levels in the rubric (typically 3-6)",
        ge=2,
        le=10
    )
    objectives: str = Field(
        "",
        description="The learning standards or objectives for the assignment"
    )
    assignment_description: str = Field(
        "",
        description="Detailed description of the assignment"
    )
    additional_customization: str = Field(
        "",
        description="Any additional customization or specific requirements for the rubric"
    )
    objectives_file_url: Optional[str] = Field(
        None,
        description="URL to a file containing standards/objectives"
    )
    objectives_file_type: Optional[FileType] = Field(
        None,
        description="Type of the objectives file"
    )
    assignment_description_file_url: Optional[str] = Field(
        None,
        description="URL to a file containing assignment description"
    )
    assignment_description_file_type: Optional[FileType] = Field(
        None,
        description="Type of the assignment description file"
    )
    lang: str = Field(
        "en",
        description="Language code for the rubric (e.g., 'en', 'es', 'fr')",
        min_length=2,
        max_length=5
    )

    @validator('objectives', 'assignment_description', pre=True, always=True)
    def check_required_fields(cls, v, values, field):
        # If both direct input and file input are empty for objectives
        if field.name == 'objectives' and not v and not values.get('objectives_file_url'):
            raise ValueError("Either objectives or objectives_file_url must be provided")
        # If both direct input and file input are empty for assignment description
        if field.name == 'assignment_description' and not v and not values.get('assignment_description_file_url'):
            raise ValueError("Either assignment_description or assignment_description_file_url must be provided")
        return v

    @validator('objectives_file_url', 'assignment_description_file_url')
    def validate_file_urls(cls, v, values, field):
        if not v:
            return v
        if not any(v.startswith(prefix) for prefix in ('http://', 'https://')):
            raise ValueError(f"{field.name} must be a valid URL starting with http:// or https://")
        return v


class RubricGenerator:
    def __init__(self, args: RubricGeneratorArgs, vectorstore_class=Chroma, prompt=None, 
                 embedding_model=None, model=None, parser=None, verbose=False):
        """
        Initialize the RubricGenerator.
        
        Args:
            args: RubricGeneratorArgs containing all necessary parameters
            vectorstore_class: Class to use for vector storage (default: Chroma)
            prompt: Optional custom prompt template
            embedding_model: Optional custom embedding model
            model: Optional custom language model
            parser: Optional custom output parser
            verbose: Whether to enable verbose logging
        """
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=RubricOutput),
            "prompt": read_text_file("prompt/rubric-generator-prompt.txt"),
            "prompt_without_context": read_text_file("prompt/rubric-generator-without-context-prompt.txt"),
            "vectorstore_class": Chroma
        }

        self.prompt = prompt or default_config["prompt"]
        self.prompt_without_context = default_config["prompt_without_context"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose
        
        # Validate arguments using Pydantic
        if not isinstance(args, RubricGeneratorArgs):
            raise ValueError("args must be an instance of RubricGeneratorArgs")
            
        # Additional validation
        if not (args.objectives or args.objectives_file_url):
            raise ValueError("Either objectives or objectives_file_url must be provided")
            
        if not (args.assignment_description or args.assignment_description_file_url):
            raise ValueError("Either assignment_description or assignment_description_file_url must be provided")

    def compile_with_context(self, documents: List[Document]):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        if self.runner is None:
            logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            logger.info(f"Vectorstore created") if self.verbose else None

            self.retriever = self.vectorstore.as_retriever()
            logger.info(f"Retriever created successfully") if self.verbose else None

            self.runner = RunnableParallel(
                {"context": self.retriever,
                "attribute_collection": RunnablePassthrough()
                }
            )

        chain = self.runner | prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain
    
    def compile_without_context(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt_without_context,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain

     
    
    def create_rubric(self, documents: Optional[List[Document]] = None) -> Dict[str, Any]:
        """
        Create a rubric based on the provided documents and arguments.
        
        Args:
            documents: Optional list of documents containing additional context.
                     If None, will use only the provided text inputs.
            
        Returns:
            dict: The generated rubric with the following structure:
                {
                    "title": str,
                    "grade_level": str,
                    "criterias": List[{
                        "criteria": str,
                        "criteria_description": List[{
                            "points": str,
                            "description": List[str]
                        }]
                    }],
                    "feedback": str
                }
            
        Raises:
            ValueError: If there's an error generating the rubric after multiple attempts
            RuntimeError: If the rubric generation fails due to validation errors
        """
        documents = documents or []
        logger.info(f"Starting rubric generation for grade level: {self.args.grade_level}")
        
        # Prepare the attribute collection for the prompt
        attribute_collection = {
            "grade_level": self.args.grade_level,
            "point_scale": self.args.point_scale,
            "objectives": self.args.objectives,
            "assignment_description": self.args.assignment_description,
            "additional_customization": self.args.additional_customization,
            "lang": self.args.lang,
            "objectives_file_url": self.args.objectives_file_url or "",
            "assignment_description_file_url": self.args.assignment_description_file_url or ""
        }

        # Log input parameters (excluding large text fields)
        log_attributes = attribute_collection.copy()
        for field in ["objectives", "assignment_description", "additional_customization"]:
            if field in log_attributes and log_attributes[field]:
                log_attributes[field] = f"[Content length: {len(log_attributes[field])} chars]"
        
        logger.info(f"Rubric generation parameters: {log_attributes}")
        logger.info(f"Processing with {len(documents)} context documents")

        # Compile the appropriate chain based on whether we have documents
        try:
            if documents:
                chain = self.compile_with_context(documents)
            else:
                chain = self.compile_without_context()
        except Exception as e:
            logger.error(f"Failed to compile rubric generation chain: {str(e)}")
            raise RuntimeError("Failed to initialize rubric generation process") from e

        attempt = 1
        max_attempts = 3
        last_error = None

        while attempt <= max_attempts:
            try:
                logger.info(f"Attempt {attempt} of {max_attempts}")
                response = chain.invoke({"attribute_collection": attribute_collection})
                
                if not response:
                    raise ValueError("Empty response from rubric generation")
                
                logger.debug(f"Raw rubric response: {response}")
                
                # Validate the response structure
                if not self.validate_rubric(response):
                    raise ValueError("Generated rubric failed validation")
                
                logger.info(f"Successfully generated rubric after {attempt} attempt(s)")
                
                # Clean up resources
                if documents and self.vectorstore:
                    if self.verbose:
                        logger.debug("Cleaning up vectorstore resources")
                    self.vectorstore.delete_collection()
                
                return cast(Dict[str, Any], response)
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed: {str(e)}")
                attempt += 1
                if attempt <= max_attempts:
                    logger.info("Retrying...")
                    continue
        
        # If we get here, all attempts failed
        error_msg = f"Failed to generate rubric after {max_attempts} attempts"
        if last_error:
            error_msg += f": {str(last_error)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    def validate_rubric(self, response: Dict[str, Any]) -> bool:
        """
        Validate the structure and content of the generated rubric.
        
        Args:
            response: The generated rubric to validate
            
        Returns:
            bool: True if the rubric is valid, False otherwise
        """
        if not isinstance(response, dict):
            logger.error("Rubric must be a dictionary")
            return False
            
        required_keys = {"title", "grade_level", "criterias", "feedback"}
        if not all(key in response for key in required_keys):
            missing = required_keys - response.keys()
            logger.error(f"Missing required keys in rubric: {missing}")
            return False
            
        if not isinstance(response.get("criterias"), list) or not response["criterias"]:
            logger.error("Rubric must contain at least one criteria")
            return False
            
        # Validate each criteria
        for criteria in response["criterias"]:
            if not isinstance(criteria, dict) or "criteria" not in criteria:
                logger.error("Each criteria must be a dictionary with a 'criteria' key")
                return False
                
            if not isinstance(criteria.get("criteria_description"), list):
                logger.error("Each criteria must have a 'criteria_description' list")
                return False
                
            # Validate each description in the criteria
            for desc in criteria["criteria_description"]:
                if not isinstance(desc, dict) or "points" not in desc or "description" not in desc:
                    logger.error("Each criteria description must have 'points' and 'description' keys")
                    return False
                    
        return True
    
class CriteriaDescription(BaseModel):
    points: str = Field(..., description="The total points gained by the student according to the point_scale an the level name")
    description: List[str] = Field(..., description="Description for the specific point on the scale")

class RubricCriteria(BaseModel):
    criteria: str = Field(..., description="name of the criteria in the rubric")
    criteria_description: List[CriteriaDescription] = Field(..., description="Descriptions for each point on the scale")
    
class RubricOutput(BaseModel):
    title: str = Field(..., description="the rubric title of the assignment based on the standard input parameter")
    grade_level: str = Field(..., description="The grade level for which the rubric is created")
    criterias: List[RubricCriteria] = Field(..., description="The grading criteria for the rubric")
    feedback: str = Field(..., description="the feedback provided by the AI model on the generated rubric")
    
