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

logger = setup_logger(__name__)

class OutlineGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, embedding_model=None, model=None, parser=None, verbose=False):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Read the prompt files
        outline_prompt_path = os.path.join(script_dir, "prompt/outline_generator_prompt.txt")
        outline_prompt_without_context_path = os.path.join(script_dir, "prompt/outline_generator_without_context_prompt.txt")
        
        with open(outline_prompt_path, 'r') as f:
            default_outline_prompt = f.read()
            
        with open(outline_prompt_without_context_path, 'r') as f:
            default_outline_prompt_without_context = f.read()
            
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=Outlines),
            "outline_prompt": default_outline_prompt,
            "outline_prompt_without_context": default_outline_prompt_without_context,
            "vectorstore_class": Chroma
        }

        self.outline_prompt = default_config["outline_prompt"]
        self.outline_prompt_without_context = default_config["outline_prompt_without_context"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose
        self.context = None
        
        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if args.topic is None: raise ValueError("Topic must be provided")
        if args.lang is None: raise ValueError("Language must be provided")

    def compile_with_context(self, documents: List[Document]):
        # Return the chain
        prompt = PromptTemplate(
            template=self.outline_prompt,
            input_variables=["instructional_level", "n_slides", "topic","context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        if self.runner is None:
            logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            logger.info(f"Vectorstore created") if self.verbose else None

            retriever = self.vectorstore.as_retriever()
            logger.info(f"Retriever created successfully") if self.verbose else None
            query = "Provide general context for the topic to create notes."
            self.context = retriever.invoke(query)
            
        chain = prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain

    
    def compile_without_context(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.outline_prompt_without_context,
            input_variables=["instructional_level", "n_slides", "topic"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain

    def generate_outline(self, documents: Optional[List[Document]]):
        logger.info("Creating the outline for the presentation") 

        if(documents):
            chain = self.compile_with_context(documents)
        else:
            chain = self.compile_without_context()


        input_parameters = {
            "instructional_level": self.args.instructional_level,
            "n_slides": self.args.n_slides,
            "topic": self.args.topic,
            "lang": self.args.lang,
            "context":self.context
        }
        logger.info(f"Input parameters: {input_parameters}")

        response = chain.invoke(input_parameters)

        logger.info(f"Generated response: {response}")

        if(documents):
            if self.verbose: print(f"Deleting vectorstore")
            self.vectorstore.delete_collection()
        return response



class Outlines(BaseModel):
    outlines: List[str] = Field(..., description="The full collection of slide outlines about the Presentation")