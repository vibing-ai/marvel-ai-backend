from typing import List, Optional
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.logger import setup_logger

logger = setup_logger(__name__)

class TextRewriterPipeline:
    """
    A pipeline for rewriting text or documents according to user-provided instructions.
    """

    def __init__(
        self,
        rewrite_instruction: str,
        text: Optional[str] = None,
        text_file_url: Optional[str] = None,
        text_file_type: Optional[str] = None,
        lang: str = "en",
    ):
        self.rewrite_instruction = rewrite_instruction
        self.text = text  # Raw text input
        self.text_file_url = text_file_url  # File URL if provided
        self.text_file_type = text_file_type
        self.lang = lang

        # Initialize the LLM (Google Gemini)
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

    def rewrite(self, docs: List[Document]) -> str:
        """
        Main entry point for rewriting content.
        If docs are provided, rewrite from those documents; otherwise, rewrite raw text.
        """
        if docs:
            logger.info("Rewriting content from documents.")
            return self._rewrite_docs(docs)

        if self.text:
            logger.info("Rewriting direct text input.")
            return self._rewrite_text(self.text)

        logger.warning("No documents or text provided for rewriting.")
        return ""

    def _rewrite_docs(self, docs: List[Document]) -> str:
        """
        Combine document contents and invoke the LLM with rewrite instructions.
        """
        content = "\n\n".join([doc.page_content for doc in docs])
        prompt = (
            f"{self.rewrite_instruction} the following document content "
            f"in language '{self.lang}':\n\n{content}"
        )
        response = self.model.invoke([prompt])
        return str(response)

    def _rewrite_text(self, text: str) -> str:
        """
        Invoke the LLM with rewrite instructions for raw text input.
        """
        prompt = (
            f"{self.rewrite_instruction} the following text "
            f"in language '{self.lang}':\n\n{text}"
        )
        response = self.model.invoke([prompt])
        return str(response)
