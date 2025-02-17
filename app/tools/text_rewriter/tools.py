from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from app.services.logger import setup_logger
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from docx import Document
import os
import csv
import pandas as pd
from fpdf import FPDF
from app.utils.document_loaders import get_docs

logger = setup_logger()

class TextRewriterArgs(BaseModel):
    text: str
    rewrite_style: str
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    lang: str = "en"

class RewrittenText(BaseModel):
    original: str = Field(..., description="Original text")
    rewritten: str = Field(..., description="Rewritten text")
    style: str = Field(..., description="Style used for rewriting")
    changes_explained: str = Field(..., description="Explanation of changes made")

class TextRewriterPipeline:
    def __init__(self, args: TextRewriterArgs, verbose: bool = False):
        self.args = args
        self.verbose = verbose
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro")

    def _create_prompt(self, text: str, style: str) -> str:
        return f"""Rewrite the following text in {style} style while maintaining its core meaning. 
        Provide the rewritten version and explain the key changes made.

        Original text: {text}
        """

    def rewrite_text(self, docs=None):
        try:
            # Process URL inputs if present
            if self.args.file_url and self.args.file_type:
                if self.args.file_type == "youtube":
                    docs = get_docs(self.args.file_url, "youtube_url", True)
                elif self.args.file_type == "website":
                    docs = get_docs(self.args.file_url, "web_url", True)
                elif self.args.file_type == "sheets":
                    docs = get_docs(self.args.file_url, "gsheet", True)

            # Validate input text
            text_to_rewrite = docs[0].page_content if docs else self.args.text
            if not text_to_rewrite or not text_to_rewrite.strip():
                raise ValueError("Text to rewrite cannot be empty")

            # Generate and validate prompt
            prompt = self._create_prompt(text_to_rewrite, self.args.rewrite_style)
            if not prompt:
                raise ValueError("Failed to create prompt")

            # Get LLM response
            response = self.llm.invoke([HumanMessage(content=prompt)])
            if not response or not response.content:
                raise ValueError("Failed to get valid response from LLM")

            # Parse response
            response_parts = response.content.split('\n\n')
            if len(response_parts) < 1:
                raise ValueError("Invalid response format")

            rewritten_text = response_parts[0].strip()
            explanation = response_parts[-1].strip() if len(response_parts) > 1 else "Changes made to match requested style"

            result = RewrittenText(
                original=text_to_rewrite,
                rewritten=rewritten_text,
                style=self.args.rewrite_style,
                changes_explained=explanation
            )
            return result

        except Exception as e:
            logger.error(f"Error in text rewriting: {str(e)}")
            raise ValueError(f"Failed to rewrite text: {str(e)}")

    def export_as_docx(self, result: RewrittenText, output_path: str):
        doc = Document()
        doc.add_heading('Text Rewriting Result', 0)

        doc.add_heading('Original Text:', level=1)
        doc.add_paragraph(result.original)

        doc.add_heading(f'Rewritten Text ({result.style} style):', level=1)
        doc.add_paragraph(result.rewritten)

        doc.add_heading('Changes Explained:', level=1)
        doc.add_paragraph(result.changes_explained)

        doc.save(output_path)

    def export_as_pdf(self, result: RewrittenText, output_path: str):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Text Rewriting Result', ln=True)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Original Text:', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, result.original)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Rewritten Text ({result.style} style):', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, result.rewritten)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Changes Explained:', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, result.changes_explained)

        pdf.output(output_path)
class TextRewriterValidator:
    @staticmethod
    def validate_text(text: str) -> bool:
        return bool(text and text.strip())

    @staticmethod
    def validate_style(style: str) -> bool:
        return bool(style and style.strip())

    @staticmethod
    def validate_language(lang: str) -> bool:
        return bool(lang and lang.strip() and len(lang) == 2)

    @staticmethod
    def validate_file_type(file_type: Optional[str]) -> bool:
        if not file_type:
            return True
        allowed_types = ["txt", "pdf", "docx", "md", "csv", "ppt", "youtube", "website", "sheets"]
        return file_type.lower() in allowed_types