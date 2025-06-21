from pydantic import BaseModel, Field
from typing import Optional, List
import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.services.logger import setup_logger

logger = setup_logger(__name__)


def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()


class TextRewriterPipeline:
    def __init__(self, args=None, model=None, embedding_model=None, vectorstore_class=Chroma, parser=None, prompt=None,
                 verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            "parser": JsonOutputParser(pydantic_object=TextRewriterOutput),
            "prompt": read_text_file("./prompt/text-rewriter-prompt.txt"),
            "prompt_without_context": read_text_file("./prompt/text-rewriter-without-context-prompt.txt"),
            "vectorstore_class": Chroma,
        }

        self.model = default_config["model"] or model
        self.embedding_model = embedding_model or default_config["embedding_model"]

        self.parser = parser or default_config["parser"]
        self.prompt = prompt or default_config["prompt"]
        self.prompt_without_context = default_config["prompt_without_context"]

        self.args, self.verbose = args, verbose

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None

        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if args.text_input is None: raise ValueError("Text input must be provided")
        if args.rewrite_instruction is None: raise ValueError("Rewrite instruction must be provided")
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
        logger.info(f"Rewriting text")
        if documents:
            chain = self.compile_with_docs(documents)
        else:
            chain = self.compile_without_docs()

        response = chain.invoke(f"""Original Text: {self.args.text_input}, 
                                Rewrite Instruction: {self.args.rewrite_instruction}, 
                                Respond in this language: {self.args.lang}""")

        if documents:
            if self.verbose: print(f"Deleting vectorstore")
            self.vectorstore.delete_collection()

        return response


class TextRewriterOutput(BaseModel):
    rewritten_text: str = Field(..., description="The rewritten text")
