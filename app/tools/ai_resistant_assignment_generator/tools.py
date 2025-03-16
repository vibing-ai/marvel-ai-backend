from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.logger import setup_logger

logger = setup_logger(__name__)

class AIResistantAssignmentGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        # Read prompt files
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Read the prompt files
        prompt_path = os.path.join(script_dir, "prompt/ai-resistant-prompt.txt")
        prompt_without_context_path = os.path.join(script_dir, "prompt/ai-resistant-without-context-prompt.txt")
        
        with open(prompt_path, 'r') as f:
            default_prompt = f.read()
            
        with open(prompt_without_context_path, 'r') as f:
            default_prompt_without_context = f.read()
            
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=AIResistantOutput),
            "prompt": default_prompt,
            "prompt_without_context": default_prompt_without_context,
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

        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if args.assignment is None: raise ValueError("Assignment must be provided")
        if args.grade_level is None: raise ValueError("Grade Level must be provided")
        if args.lang is None: raise ValueError("Language must be provided")


    def compile_with_docs(self, documents: List[Document]):
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
    
    def compile_without_docs(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt_without_context,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain

    def create_assignments(self, documents: Optional[List[Document]]):
        logger.info(f"Creating the AI-Resistant assignments")

        if(documents):
            chain = self.compile_with_docs(documents)
        else:
            chain = self.compile_without_docs()

        response = chain.invoke(f"""Assignment Description: {self.args.assignment}, 
                                Grade Level: {self.args.grade_level}, 
                                Language (YOU MUST RESPOND IN THIS LANGUAGE): {self.args.lang}""")

        if(documents):
            if self.verbose: print(f"Deleting vectorstore")
            self.vectorstore.delete_collection()

        return response

class AIResistanceIdea(BaseModel):
    title: str = Field(..., description="The main title of the idea")
    assignment_description: str = Field(..., description="Detailed description of the modified assignment")
    explanation: str = Field(..., description="Explanation of how this modification makes the assignment AI-resistant")

class AIResistantOutput(BaseModel):
    topic: str = Field(..., description="Topic or subject related to the assignment")
    grade_level: str = Field(..., description="Educational level to which the assignment is directed")
    ideas: List[AIResistanceIdea] = Field(..., description="List of 3 ideas to make the assignment AI-resistant, including explanation")