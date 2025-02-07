import os
from typing import List, Optional

from pydantic import BaseModel, Field

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from app.services.logger import setup_logger

logger = setup_logger(__name__)


def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()


class AITextRewriter:
    def __init__(
            self,
            args=None,
            vectorstore_class=Chroma,
            prompt=None,
            embedding_model=None,
            model=None,
            parser=None,
            verbose=False
    ):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=AITextRewriterOutput),
            "prompt": read_text_file("prompt/ai-text-rewriter-prompt.txt"),
            "prompt_without_context": read_text_file("prompt/ai-text-rewriter-without-context-prompt.txt"),
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
        if args.original_text is None: raise ValueError("Text must be provided")
        if args.instruction is None: raise ValueError("Instructions must be provided")
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

    def rewrite_text(self, documents: Optional[List[Document]]):
        logger.info(f"Creating the AI-TextRewriter assignments")
        if (documents):
            chain = self.compile_with_docs(documents)
        else:
            chain = self.compile_without_docs()

        response = chain.invoke(f"""Text: {self.args.original_text}, 
                                Instruction: {self.args.instruction}, 
                                Language (YOU MUST RESPOND IN THIS LANGUAGE): {self.args.lang}""")

        if (documents):
            if self.verbose: print(f"Deleting vectorstore")
            self.vectorstore.delete_collection()

        return response


class AITextRewriterOutput(BaseModel):
    rewritten_text: str = Field(..., description="The rewriting text")
