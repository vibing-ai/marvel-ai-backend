from pydantic import BaseModel, Field
from typing import Optional
from app.services.logger import setup_logger
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from docx import Document
import os
import csv
import pandas as pd
from fpdf import FPDF
from app.utils.document_loaders import get_docs
import re

logger = setup_logger()


# ------------------ Post-Processing Functions ------------------

def post_process_business_email(output: str) -> str:
    """
    Post-process the LLM output for 'business_email' style.
    This function forces the desired line breaks by looking for the defined XML-like tags.
    It reconstructs the email so that each section appears on its own, with proper blank lines.
    """
    # Extract each section with regex:
    subject_pattern = r"<SubjectLine>(.*?)</SubjectLine>"
    greeting_pattern = r"<Greeting>(.*?)</Greeting>"
    body_pattern = r"<Body>(.*?)</Body>"
    closing_pattern = r"<Closing>(.*?)</Closing>"

    subject_match = re.search(subject_pattern, output, re.DOTALL)
    greeting_match = re.search(greeting_pattern, output, re.DOTALL)
    body_match = re.search(body_pattern, output, re.DOTALL)
    closing_match = re.search(closing_pattern, output, re.DOTALL)

    subject_line = subject_match.group(1).strip() if subject_match else "No Subject Found"
    greeting = greeting_match.group(1).strip() if greeting_match else "Dear [Recipient Name],"
    body_text = body_match.group(1).strip() if body_match else "(No body found)"
    closing_text = closing_match.group(1).strip() if closing_match else "Best regards,\n[Your Name]"

    # Construct final email with guaranteed blank lines between sections
    final_email = (
        f"Subject: {subject_line}\n\n"
        f"{greeting}\n\n"
        f"{body_text}\n\n"
        f"{closing_text}"
    )
    return final_email


def parse_business_email_tags(raw_text: str) -> (str, str):
    """
    Parses the raw output for business_email style.
    Returns a tuple (final_email, changes_text) where final_email is post-processed.
    """
    # Extract <Changes> content separately.
    changes_pattern = r"<Changes>(.*?)</Changes>"
    changes_match = re.search(changes_pattern, raw_text, re.DOTALL)
    changes_text = changes_match.group(1).strip() if changes_match else "No bullet points or explanation provided."

    # Post-process the rest for proper formatting.
    final_email = post_process_business_email(raw_text)
    return final_email, changes_text


def parse_formal_tags(raw_text: str) -> (str, str):
    """
    Parses the raw output for 'formal' style which should be enclosed in <FormalText> and <Changes> tags.
    Returns a tuple (final_text, changes_text).
    """
    formal_pattern = r"<FormalText>(.*?)</FormalText>"
    changes_pattern = r"<Changes>(.*?)</Changes>"

    formal_match = re.search(formal_pattern, raw_text, re.DOTALL)
    changes_match = re.search(changes_pattern, raw_text, re.DOTALL)

    formal_text = formal_match.group(1).strip() if formal_match else "(No formal text found)"
    changes_text = changes_match.group(1).strip() if changes_match else "No bullet points or explanation provided."

    return formal_text, changes_text


# ------------------ Data Models ------------------

class TextRewriterArgs(BaseModel):
    text: str
    rewrite_style: str
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    lang: str = "en"
    reading_level: Optional[str] = None       # e.g., "Elementary", "Middle School", etc.
    excluded_terms: Optional[str] = None        # Comma-separated list of terms to remain unchanged


class RewrittenText(BaseModel):
    original: str = Field(..., description="Original text")
    rewritten: str = Field(..., description="Rewritten text")
    style: str = Field(..., description="Style used for rewriting")
    changes_explained: str = Field(..., description="Explanation of changes made")


# ------------------ Pipeline Implementation ------------------

class TextRewriterPipeline:
    def __init__(self, args: TextRewriterArgs, verbose: bool = False):
        self.args = args
        self.verbose = verbose
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", callbacks=[])

    def _create_prompt(self, text: str, style: str) -> str:
        """
        Constructs the prompt for the LLM.
        For 'business_email', instruct the model to output ONLY the specified XML-like tags.
        For 'formal', instruct the model to output <FormalText> and <Changes> tags.
        For other styles, use a standard bullet-point approach.
        """
        if style == "business_email":
            prompt = (
                "You are a text rewriting assistant. Please rewrite the following text as a polite, concise, "
                "and well-structured business email. Use ONLY the following XML-like tags, and include no text outside them:\n\n"
                "<SubjectLine>...</SubjectLine>\n"
                "<Greeting>...</Greeting>\n"
                "<Body>...</Body>\n"
                "<Closing>...</Closing>\n"
                "<Changes>...</Changes>\n\n"
                "Follow these rules:\n"
                "- Each section must be enclosed in its respective tag.\n"
                "- Ensure that each sentence ends with proper punctuation.\n"
                "- Separate paragraphs in <Body> with exactly one blank line.\n\n"
                f"Original text:\n{text}\n\n"
            )
        elif style == "formal":
            prompt = (
                "You are a text rewriting assistant. Please rewrite the following text in a polite, refined, and formal tone. "
                "Use ONLY the following tags in your output:\n\n"
                "<FormalText>...</FormalText>\n"
                "<Changes>...</Changes>\n\n"
                "Follow these rules:\n"
                "- The entire rewritten text must be enclosed within <FormalText>.\n"
                "- Each main idea should be in its own paragraph (separated by a blank line).\n"
                "- All bullet points must be inside <Changes>, with each bullet starting with '-' or '•'.\n\n"
                f"Original text:\n{text}\n\n"
            )
        else:
            prompt = (
                f"You are a text rewriting assistant. Please rewrite the following text in '{style}' style, "
                "preserving its meaning and using proper punctuation. Avoid scientific or overly complex synonyms unless they are in the original text.\n\n"
                f"Original text:\n{text}\n\n"
                "After the rewritten text, skip one line and provide bullet points summarizing the key changes."
            )

        # Append advanced educator instructions if provided.
        if self.args.reading_level:
            prompt += f"\nAim for a {self.args.reading_level} reading level."
        if self.args.excluded_terms:
            prompt += f"\nDo not alter these terms: {self.args.excluded_terms}."

        return prompt

    def rewrite_text(self, docs=None):
        try:
            if self.args.file_url and self.args.file_type:
                docs = get_docs(self.args.file_url, self.args.file_type, True)
            text_to_rewrite = docs[0].page_content if docs else self.args.text
            if not text_to_rewrite or not text_to_rewrite.strip():
                raise ValueError("Text to rewrite cannot be empty")

            prompt = self._create_prompt(text_to_rewrite, self.args.rewrite_style)
            if not prompt:
                raise ValueError("Failed to create prompt")

            response = self.llm.invoke([HumanMessage(content=prompt)])
            if not response or not response.content:
                raise ValueError("Failed to get valid response from LLM")

            logger.info(f"Raw LLM response: {response.content}")

            if self.args.rewrite_style == "business_email":
                final_email, changes_text = parse_business_email_tags(response.content)
                # Apply post-processing for business_email formatting
                final_email = post_process_business_email(final_email)
                return RewrittenText(
                    original=text_to_rewrite,
                    rewritten=final_email,
                    style=self.args.rewrite_style,
                    changes_explained=changes_text if changes_text.strip() else "No bullet points provided."
                )
            elif self.args.rewrite_style == "formal":
                final_text, changes_text = parse_formal_tags(response.content)
                return RewrittenText(
                    original=text_to_rewrite,
                    rewritten=final_text,
                    style=self.args.rewrite_style,
                    changes_explained=changes_text
                )
            else:
                lines = [line.strip() for line in response.content.split('\n') if line.strip()]
                if not lines:
                    raise ValueError("LLM returned an empty or invalid format response.")

                rewritten_lines = []
                changes_lines = []
                found_bullet = False
                for line in lines:
                    if line.startswith('-') or line.startswith('•'):
                        found_bullet = True
                    if found_bullet:
                        changes_lines.append(line)
                    else:
                        rewritten_lines.append(line)

                rewritten_text = " ".join(rewritten_lines).strip()
                explanation = "\n".join(changes_lines).strip()

                if not explanation:
                    explanation = "No bullet points or explanation provided."
                if not rewritten_text:
                    rewritten_text = text_to_rewrite
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
        allowed_types = [
            "txt", "pdf", "docx", "md", "csv", "ppt", "youtube", "website", "sheets"
        ]
        return file_type.lower() in allowed_types






