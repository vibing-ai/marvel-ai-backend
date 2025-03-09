from typing import List, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.summarize.chain import load_summarize_chain
from app.services.logger import setup_logger
#from langchain_core.utils import setup_logger

logger = setup_logger(__name__)

class NotesGeneratorPipeline:
    """
    A pipeline for generating notes using either:
    1) A vector store approach for documents (using a retrieval-based approach 
    plus a generative LLM (Google Gemini)) OR
    2) Direct text summarization (no vector store).
    """

    def __init__(
        self,
        topic: str,
        page_layout: str,
        text: Optional[str] = None,
        text_file_url: Optional[str] = None,
        text_file_type: Optional[str] = None,
        lang: str = "en",
    ):
        self.topic = topic
        self.page_layout = page_layout
        self.text = text  # raw text input
        self.text_file_url = text_file_url  # file URL if provided
        self.text_file_type = text_file_type
        self.lang = lang

        # Initialize the LLM (Google Gemini)
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
        # Initialize embeddings for Chroma
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        # self.vectorstore = None
        # self.retriever = None

    def generate_notes(self, docs: List[Document]) -> str:
        """
        Main entry point for generating notes.
        Generate notes if documents exist; we build a vector store + retrieval pipeline. 
        if text is present (without docs), we do a direct text summarization.
        """

        # Check if we document is loaded
        has_docs = bool(docs)
        # Check if the user provided raw text
        has_text = bool(self.text)

        # For docs, we build a vector store and summarize
        if has_docs:
            logger.info("Generating notes from documents using a vector store.")
            return self.generate_from_docs(docs)

        # For raw text without doc, we do direct summarization
        if has_text:
            logger.info("Generating notes directly from 'text' (no vector store).")
            return self.generate_from_text(self.text)

        # If neither docs nor text, nothing to summarize
        return "No documents or text provided."
    
    def generate_from_docs(self, docs: List[Document]) -> str:
        """
        Summarize documents using a vector store + summarization chain.
        """
        # Build a vector
        self.vectorstore = Chroma.from_documents(docs, self.embedding_model)
        self.retriever = self.vectorstore.as_retriever()

        # Summarize chain; focusing on the topic, text & language if needed
        # Here, we are using "map_reduce" chain for summarization (other options can be considered)
        summarize_chain = load_summarize_chain(self.model, chain_type="map_reduce")

        # Prompt for the summarization
        prompt_template = (
            f"Summarize these documents focusing on '{self.topic}'. "
            f"Page layout: {self.page_layout}. Language: {self.lang}"
        )
        #Running the chain
        result = summarize_chain.run({
            "input_documents": docs,
            "question": prompt_template
        })
        return result
    
    def generate_from_text(self, raw_text: str) -> str:
        """
        Summarize raw text only (no vector store).
        """
        prompt = (
            f"Summarize the following text focusing on '{self.topic}' "
            f"with a page layout of '{self.page_layout}' in language '{self.lang}':\n\n"
            f"{raw_text}"
        )
        response = self.model.invoke([prompt])
        return str(response) # return the response as a string or response.content if needed