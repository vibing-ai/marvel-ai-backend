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
from app.tools.utils.tool_utilities import read_text_file

logger = setup_logger(__name__)

class AIConnectWithThemGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=RecommendationsOutput),
            "prompt": read_text_file("prompt/connect-with-them-prompt.txt"),
            "prompt_without_context": read_text_file("prompt/connect-with-them-without-context-prompt.txt"),
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
        if args.grade_level is None: raise ValueError("Grade Level must be provided")
        if args.task_description is None: raise ValueError("Task Description must be provided")
        if args.students_description is None: raise ValueError("Student Description Level must be provided")
        if args.lang is None: raise ValueError("Language must be provided")


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

        if self.verbose: logger.info(f"Chain compilation complete")

        return chain
    
    def compile_without_context(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt_without_context,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser

        if self.verbose: logger.info(f"Chain compilation complete")

        return chain

    def generate_suggestion(self, documents: Optional[List[Document]]):
        if self.verbose: logger.info(f"Creating the AI Connect with Them suggestions")

        if(documents):
            chain = self.compile_with_context(documents)
        else:
            chain = self.compile_without_context()

        response = chain.invoke(f"""Grade Level: {self.args.grade_level},
          Task Description: {self.args.task_description},
          Student's Description: {self.args.students_description},
          Language (YOU MUST RESPOND IN THIS LANGUAGE): {self.args.lang}""")

        if(documents):
            if self.verbose: logger.info(f"Deleting vectorstore")
            self.vectorstore.delete_collection()
    
        return response

class Recommendation(BaseModel):
    title: str = Field(..., description="The title of the recommendation")
    project_overview: str = Field(..., description="A detailed description of the project or activity recommendation. It must be a large paragraph.")
    rationale: str = Field(..., description="An explanation of why this recommendation is relevant to the students' interests or background.")
    difficulty_level: str = Field(..., description="The difficulty level of the project (e.g., easy, moderate, challenging).")
    required_tools: List[str] = Field(..., description="A list of tools, software, or resources required to complete the project.")
    estimated_time: str = Field(..., description="The estimated time to complete the project or activity.")

class RecommendationsOutput(BaseModel):
    recommendations: List[Recommendation] = Field(..., description="A list of personalized recommendations based on the input.")