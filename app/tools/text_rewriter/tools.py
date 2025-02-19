from typing import List, Dict
import os

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.services.logger import setup_logger

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class TextRewriter:
    def __init__(self, rewrite_instructions, lang='en', vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=TextRewriterOutput),
            "prompt": read_text_file("prompt/text_rewriter_prompt.txt"),
            "vectorstore_class": Chroma
        }
        
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.content, self.runner = None, None, None
        self.rewrite_instructions = rewrite_instructions
        self.lang = lang
        self.verbose = verbose
        
        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
    
    def compile(self, raw_text, documents: List[Document]):
        if (raw_text is None or raw_text == "") and (documents is None or len(documents) == 0): raise ValueError("Either plain text or documents must be provided")
        
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["content", "lang", "rewrite_instructions"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        if self.runner is None:
            if(documents is not None):
                logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
                self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            else:
                self.vectorstore = self.vectorstore_class.from_texts([raw_text], self.embedding_model)
                
            logger.info(f"Vectorstore created") if self.verbose else None

            self.content = self.vectorstore.as_retriever()
            logger.info(f"Retriever created successfully {self.content}") if self.verbose else None

            self.runner = RunnableParallel(
                {"content": self.content, 
                "lang": lambda _: self.lang,
                "rewrite_instructions": lambda _: self.rewrite_instructions
                }
            )
        
        chain = self.runner | prompt | self.model | self.parser
        
        if self.verbose: logger.info(f"Chain compilation complete")
        
        return chain

    def validate_response(self, response: Dict) -> bool:
        try:
            # Assuming the response is already a dictionary
            if isinstance(response, dict):
                if 'rewritten_text' in response:
                    return True
            return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False
    
    def rewrite(self, raw_text, documents: List[Document]) -> Dict:
        if self.verbose: logger.info(f"Rewriting text...")
        
        chain = self.compile(raw_text, documents)
        
        response = {}
        attempts = 0
        max_attempts = 5  # Allow for more attempts to generate questions

        while attempts < max_attempts:
            response = chain.invoke(f"Rewrite Instructions: {self.rewrite_instructions}, Lang: {self.lang}")
            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")

            # Directly check if the response format is valid
            if self.validate_response(response):
                if self.verbose:
                    logger.info(f"Rewritten text generated successfully: {response}")
                break
            else:
                if self.verbose:
                    logger.warning(f"Invalid response format. Attempt {attempts + 1} of {max_attempts}")
            
            # Move to the next attempt regardless of success to ensure progress
            attempts += 1

        # Log if no response generated
        if response == "":
            logger.error(f"Unable to rewrite text")
        
        if self.verbose: logger.info(f"Deleting vectorstore")
        self.vectorstore.delete_collection()
        
        # Return the list of questions
        return response

class TextRewriterOutput(BaseModel):
    rewritten_text: str = Field(description="The rewritten text")