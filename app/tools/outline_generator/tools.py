
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.schemas import OutlineGeneratorArgs
from app.services.logger import setup_logger

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class OutlineOutput(BaseModel):
    """Output model for the outline generator."""
    slides: List[str] = Field(..., description="List of slide titles in the outline")

class OutlineGenerator:
    """Class to generate slide outlines based on user inputs."""
    
    def __init__(self, args: OutlineGeneratorArgs, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        """Initialize the outline generator with arguments and optional verbosity."""
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=OutlineOutput),
            "prompt": read_text_file("prompt/outline-generator-prompt.txt"),
            "prompt_without_context": read_text_file("prompt/outline-generator-without-context-prompt.txt"),
            "vectorstore_class": Chroma
        }

        self.args = args
        self.verbose = verbose
        self.prompt = prompt or default_config["prompt"]
        self.prompt_without_context = default_config["prompt_without_context"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        
        self.vectorstore, self.retriever, self.runner = None, None, None
        
        # Validation
        if args.context is None: 
            raise ValueError("Topic/Context must be provided")
        if args.level is None: 
            raise ValueError("Educational level must be provided")
        if args.num_slides is None or int(args.num_slides) < 3: 
            raise ValueError("Number of slides must be at least 3")

    def compile_with_context(self, documents: List[Document]):
        # Create a prompt template with document context
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["context", "level", "num_slides", "doc_content"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        if self.runner is None:
            logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            logger.info(f"Vectorstore created") if self.verbose else None

            self.retriever = self.vectorstore.as_retriever()
            logger.info(f"Retriever created successfully") if self.verbose else None

            self.runner = RunnableParallel(
                {"doc_content": self.retriever,
                "context": RunnablePassthrough(),
                "level": RunnablePassthrough(),
                "num_slides": RunnablePassthrough()
                }
            )

        chain = self.runner | prompt | self.model | self.parser
        logger.info(f"Chain compilation complete with context")
        return chain
    
    def compile_without_context(self):
        # Create a prompt template without document context
        prompt = PromptTemplate(
            template=self.prompt_without_context,
            input_variables=["context", "level", "num_slides"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser
        logger.info(f"Chain compilation complete without context")
        return chain

    def create_outline(self, docs=None):
        """Generate a structured outline with the specified number of slides."""
        try:
            logger.info(f"Creating outline for topic: {self.args.context}")

            # Decide which chain to use based on whether we have documents
            if docs:
                chain = self.compile_with_context(docs)
                # Log the input parameters for the chain with context
                input_parameters = self.args.context
            else:
                chain = self.compile_without_context()
                # Create input parameters for the chain without context
                input_parameters = {
                    "context": self.args.context,
                    "level": self.args.level,
                    "num_slides": str(self.args.num_slides)
                }
            
            # Log the input
            if self.verbose:
                logger.info(f"Input parameters: {input_parameters}")

            # Generate outline with retries
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    response = chain.invoke(input_parameters)
                    logger.info(f"Outline generated on attempt #{attempt}")
                    
                    # Validate the response
                    if "slides" not in response or len(response["slides"]) == 0:
                        logger.warning(f"Invalid response, missing slides. Retrying...")
                        continue
                        
                    # Check if we have the correct number of slides
                    if len(response["slides"]) != int(self.args.num_slides):
                        logger.warning(f"Expected {self.args.num_slides} slides but got {len(response['slides'])}. Retrying...")
                        continue
                        
                    # Check for generic slide titles
                    generic_count = sum(1 for title in response["slides"] if title.lower().startswith("slide "))
                    if generic_count > 0:
                        logger.warning(f"Detected {generic_count} generic slide titles. Retrying...")
                        continue
                        
                    # If we got here, the response is valid
                    break
                    
                except Exception as e:
                    logger.error(f"Error during outline generation attempt #{attempt}: {str(e)}")
                    if attempt == max_attempts:
                        raise ValueError(f"Failed to generate outline after {max_attempts} attempts: {str(e)}")
            
            # Clean up vectorstore if used
            if docs and self.vectorstore:
                if self.verbose:
                    logger.info("Deleting vectorstore")
                self.vectorstore.delete_collection()
                
            return response
            
        except Exception as e:
            logger.error(f"Error in outline generation: {str(e)}")
            raise ValueError(f"Failed to generate outline: {str(e)}")
            
    def _build_prompt(self, context, doc_content):
        """Build the prompt for the AI model."""
        prompt = f"""
        You are an educational content specialist. Create a detailed and specific outline for a presentation with {self.args.num_slides} slides on the topic: "{self.args.context}" for {self.args.level} level education.

        Context:
        {context}

        Additional context information:
        {doc_content if doc_content else "No additional context provided."}

        Output Requirements:
        1. Generate exactly {self.args.num_slides} slide titles.
        2. Each slide title MUST be specific to the topic "{self.args.context}" - generic titles like "Slide 1" are NOT acceptable.
        3. Create descriptive, informative titles that clearly indicate the content of each slide.
        4. Ensure titles are educational and appropriate for {self.args.level} level.
        5. Follow a logical flow from introduction to specific subtopics to conclusion.
        6. Format your response as a JSON array of strings ONLY (no explanation text).
        
        Return only the JSON array of slide titles.
        """
        return prompt
    
    def _process_response(self, response_text):
        """Process the AI response to extract the slide titles."""
        # This method is kept for backward compatibility but functionality 
        # is now handled by the JsonOutputParser
        return response_text
