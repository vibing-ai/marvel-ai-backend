from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.documents import Document
from typing import Optional, List, Union
from app.services.logger import setup_logger
from pydantic import BaseModel, Field

logger = setup_logger(__name__)

# Define Models to Match the Presentation Tool
class BulletPoints(BaseModel):
    title: str = Field(..., description="The title of the notes section")
    points: List[str] = Field(..., description="Key bullet points extracted from the content")

class Paragraph(BaseModel):
    title: str = Field(..., description="The title of the notes section")
    content: str = Field(..., description="A well-structured paragraph summarizing the content")

class Table(BaseModel):
    title: str = Field(..., description="The title of the table section")
    headers: List[str] = Field(..., description="Column headers for the table")
    rows: List[List[str]] = Field(..., description="Table rows containing structured data")
class GenerateNotesOutput(BaseModel):
    title: str = Field(..., description="Title of the generated notes")
    notes: BulletPoints | Paragraph | Table = Field(..., description="Structured notes generated based on the content")

class NoteGeneratorPipeline:
    def __init__(self, args=None , verbose=False):       
        self.args = args
        self.verbose = verbose
        """Dynamically selects the correct output schema based on page_layout."""
        layout_map = {
            "bullet_points": BulletPoints,
            "paragraph": Paragraph,
            "table": Table
        }

        selected_format = layout_map.get(self.args.page_layout)
        self.parser = JsonOutputParser(pydantic_object=selected_format)   
        
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.vectorstore_class = Chroma
        self.vectorstore = None
        self.retriever = None

    def compile_vectorstore(self, documents: List[Document]):
        """Creates a vector store for document retrieval."""
        if self.verbose:
            logger.info("Creating vectorstore from documents...")
            
        self.vectorstore = self.vectorstore_class.from_documents(
            documents, 
            GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        )
        self.retriever = self.vectorstore.as_retriever()
        
        if self.verbose:
            logger.info("Vectorstore and retriever created successfully.")

    def generate_context(self, query):
        """Retrieves relevant context from the vector database."""
        return self.retriever.invoke(query)

    def compile_pipeline(self):
        """Creates prompt templates for different layouts."""
        """Creates prompt templates for structured note generation."""
        prompt_template = PromptTemplate(
            template=(
                "Generate structured notes in {layout} format focusing on: {focus}. "
                "Use the following text: {context}. "
                "Ensure clarity, coherence, and well-structured content. "
                "Respond in the {lang} language. "
                "Your response must follow this JSON format: {format_instructions}"
             ),
            input_variables=["layout", "focus", "context", "lang"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        return prompt_template | self.model | self.parser

    def generate_notes(self, documents: Optional[List[Document]]):
        """Generates notes based on the selected layout."""
        if documents:
            self.compile_vectorstore(documents)
            query = "Provide general context for the topic to create notes."
            context = self.generate_context(query)
        else:
            context = ""

        # Compile the processing pipeline
        pipeline = self.compile_pipeline()

        # Prepare inputs for the AI model
        inputs = {
            "layout": self.args.page_layout,
            "focus": self.args.focus,
            "context": context,
            "lang": self.args.lang,
        }

        try:
            result = pipeline.invoke(inputs)
            
            if self.verbose:
                logger.info("Notes successfully generated.")
            return result
        except Exception as e:
            logger.error(f"Error generating notes: {e}")
            raise ValueError("Failed to generate notes.")
