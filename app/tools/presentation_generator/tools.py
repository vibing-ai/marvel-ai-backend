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

class PresentationGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        # Read prompt files
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Read the prompt files
        prompt_path = os.path.join(script_dir, "prompt/presentation-generator-prompt.txt")
        prompt_without_context_path = os.path.join(script_dir, "prompt/presentation-generator-without-context-prompt.txt")
        
        with open(prompt_path, 'r') as f:
            default_prompt = f.read()
            
        with open(prompt_without_context_path, 'r') as f:
            default_prompt_without_context = f.read()
            
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=FullPresentation),
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
        if args.grade_level is None: raise ValueError("Grade Level must be provided")
        if args.n_slides is None: raise ValueError("Number of Slides must be provided")
        if int(args.n_slides) < 1 or int(args.n_slides) > 10:
            raise ValueError("Number must be between 1 and 10.")
        if args.topic is None: raise ValueError("Topic must be provided")
        if args.objectives is None: raise ValueError("Objectives must be provided")
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

    def generate_presentation(self, documents: Optional[List[Document]]):
        logger.info(f"Creating the Presentation")

        if(documents):
            chain = self.compile_with_context(documents)
        else:
            chain = self.compile_without_context()

        input_parameters = (
            f"Grade Level: {self.args.grade_level}, "
            f"Number of Slides: {self.args.n_slides+1 if self.args.n_slides>9 else self.args.n_slides}, "
            f"Topic: {self.args.topic}, "
            f"Standard/Objectives: {self.args.objectives}, "
            f"Additional Comments: {self.args.additional_comments}, "
            f"Language (YOU MUST RESPOND IN THIS LANGUAGE): {self.args.lang}"
        )

        response = chain.invoke(input_parameters)

        logger.info(f"Generated response: {response}")

        if(documents):
            if self.verbose: print(f"Deleting vectorstore")
            self.vectorstore.delete_collection()

        return response

class Slide(BaseModel):
    title: str = Field(..., description="The title of the Slide")
    content: str = Field(..., description="The content of the Slide. It must be the actual context, not simple indications")
    suggestions: str = Field(..., description="""Suggestions for visual elements (e.g., charts, images, layouts) 
                             that enhance understanding and engagement (ONLY IF NEEDED).""")

class FullPresentation(BaseModel):
    main_title: str = Field(..., description="The main title of the Presentation")
    list_slides: List[Slide] = Field(..., description="The full collection of slides about the Presentation")