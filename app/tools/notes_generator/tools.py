from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.logger import setup_logger

logger = setup_logger(__name__)

class NotesGeneratorPipeline:
    """
    A pipeline for generating structured notes from text or documents.

    Attributes:
        verbose (bool): Enables detailed logging if set to True.
        args (Optional[Any]): Configuration arguments for the pipeline.
        model (GoogleGenerativeAI): AI model for text generation.
        embedding_model (GoogleGenerativeAIEmbeddings): Model for embeddings.
        vectorstore_class (Chroma): Vector database for document retrieval.
        parsers (Dict[str, JsonOutputParser]): JSON output parsers for different formats.
        vectorstore (Optional[Chroma]): Stores document embeddings for retrieval.
        retriever (Optional[Any]): Mechanism to retrieve relevant documents.
    """

    def __init__(self, args: Optional[Any] = None, verbose: bool = False) -> None:
        """
        Initializes the NotesGeneratorPipeline.

        Args:
            args (Optional[Any]): Configuration arguments for the pipeline.
            verbose (bool): Enables detailed logging if set to True.
        """
        self.verbose: bool = verbose
        self.args: Optional[Any] = args
        self.model: GoogleGenerativeAI = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.embedding_model: GoogleGenerativeAIEmbeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore_class: Chroma = Chroma
        self.parsers: Dict[str, JsonOutputParser] = {
            "summary": JsonOutputParser(pydantic_object=Summary),
            "bullet_points": JsonOutputParser(pydantic_object=BulletPoints),
            "table": JsonOutputParser(pydantic_object=StructuredTable)
        }
        self.vectorstore: Optional[Chroma] = None
        self.retriever: Optional[Any] = None

    def compile_vectorstore(self, documents: List[Document]) -> None:
        """
        Creates a vectorstore from the given documents for retrieval.

        Args:
            documents (List[Document]): List of documents to store and retrieve context from.
        """
        if self.verbose:
            logger.info("Creating vectorstore from documents...")
        self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
        self.retriever = self.vectorstore.as_retriever()
        if self.verbose:
            logger.info("Vectorstore and retriever created successfully.")

    def compile_pipeline(self) -> RunnableParallel:
        """
        Compiles a processing pipeline using AI-generated structured notes.

        Returns:
            RunnableParallel: A parallel pipeline containing different processing branches.
        """
        prompts: Dict[str, PromptTemplate] = {
            "summary": PromptTemplate(
                template="Summarize the content related to {focus}. Respond in JSON format: \n{format_instructions}",
                input_variables=["focus"],
                partial_variables={"format_instructions": self.parsers["summary"].get_format_instructions()},
            ),
            "bullet_points": PromptTemplate(
                template="Convert the content into bullet points focusing on {focus}. Respond in JSON format: \n{format_instructions}",
                input_variables=["focus"],
                partial_variables={"format_instructions": self.parsers["bullet_points"].get_format_instructions()},
            ),
            "table": PromptTemplate(
                template="Organize key information about {focus} into a structured table. Respond in JSON format: \n{format_instructions}",
                input_variables=["focus"],
                partial_variables={"format_instructions": self.parsers["table"].get_format_instructions()},
            )
        }
        chains: Dict[str, Any] = {key: prompt | self.model | self.parsers[key] for key, prompt in prompts.items()}
        return RunnableParallel(branches=chains)

    def generate_notes_executor(self, documents: Optional[List[Document]]) -> Dict[str, Any]:
        """
        Generates structured notes from input documents.

        Args:
            documents (Optional[List[Document]]): Documents to process for note generation.

        Returns:
            Dict[str, Any]: Dictionary containing structured notes in different formats.
        """
        if documents:
            self.compile_vectorstore(documents)

        pipeline: RunnableParallel = self.compile_pipeline()

        inputs: Dict[str, str] = {
            "focus": self.args.focus,
        }
        results: Dict[str, Dict[str, Any]] = pipeline.invoke(inputs)
        notes: Dict[str, Any] = {
            "summary": results["branches"]["summary"]["text"],
            "bullet_points": results["branches"]["bullet_points"]["points"],
            "table": results["branches"]["table"]["rows"],
        }
        if self.verbose:
            logger.info("Notes successfully generated.")
        return notes

# Models for structured output

class Summary(BaseModel):
    """Represents a textual summary."""
    text: str

class BulletPoints(BaseModel):
    """Represents bullet points extracted from content."""
    points: List[str]

class TableRow(BaseModel):
    """Represents a single row of a structured table."""
    column1: str
    column2: str

class StructuredTable(BaseModel):
    """Represents a structured table with multiple rows."""
    rows: List[TableRow]
