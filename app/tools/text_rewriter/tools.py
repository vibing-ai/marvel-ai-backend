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
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", callbacks=[])

    def _create_prompt(self, text: str, style: str) -> str:
        """
        If you're using a separate .txt file for your prompt, you can load it here.
        Otherwise, this inline prompt is a placeholder.
        """
        return (
            f"You are a text rewriting assistant. Please rewrite the following text in {style} style "
            f"while preserving its meaning, avoiding scientific synonyms unless the original text used them.\n\n"
            f"{text}\n\n"
            "After the rewritten text, skip one line and provide bullet points for any changes."
        )

    def rewrite_text(self, docs=None):
        try:
            # Handle file input if provided
            if self.args.file_url and self.args.file_type:
                if self.args.file_type == "youtube":
                    docs = get_docs(self.args.file_url, "youtube_url", True)
                elif self.args.file_type == "website":
                    docs = get_docs(self.args.file_url, "web_url", True)
                elif self.args.file_type == "sheets":
                    docs = get_docs(self.args.file_url, "gsheet", True)

            # Validate text
            text_to_rewrite = docs[0].page_content if docs else self.args.text
            if not text_to_rewrite or not text_to_rewrite.strip():
                raise ValueError("Text to rewrite cannot be empty")

            # Create prompt
            prompt = self._create_prompt(text_to_rewrite, self.args.rewrite_style)
            if not prompt:
                raise ValueError("Failed to create prompt")

            # Invoke LLM
            response = self.llm.invoke([HumanMessage(content=prompt)])
            if not response or not response.content:
                raise ValueError("Failed to get valid response from LLM")

            # Debug log the raw LLM response
            logger.info(f"Raw LLM response: {response.content}")

            # Split on line breaks, ignoring empty lines
            lines = [line.strip() for line in response.content.split('\n') if line.strip()]
            if not lines:
                raise ValueError("LLM returned an empty or invalid format response.")

            # We'll collect lines for the rewritten text until we see a bullet
            rewritten_lines = []
            changes_lines = []
            found_bullet = False

            for line in lines:
                # If line starts with '-' or '•', treat it as a bullet
                if line.startswith('-') or line.startswith('•'):
                    found_bullet = True

                if found_bullet:
                    changes_lines.append(line)
                else:
                    rewritten_lines.append(line)

            # Combine the rewritten text lines
            rewritten_text = " ".join(rewritten_lines).strip()
            # Combine changes
            explanation = "\n".join(changes_lines).strip()

            # Fallback if no bullet lines were found
            if not explanation:
                explanation = "No bullet points or explanation provided."

            # If the rewritten text is empty, revert to original
            if not rewritten_text:
                rewritten_text = text_to_rewrite

            # If the model didn't change anything, add a small note
            if rewritten_text == text_to_rewrite:
                rewritten_text = f"{text_to_rewrite} ({self.args.rewrite_style} version)"

            return RewrittenText(
                original=text_to_rewrite,
                rewritten=rewritten_text,
                style=self.args.rewrite_style,
                changes_explained=explanation
            )

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
