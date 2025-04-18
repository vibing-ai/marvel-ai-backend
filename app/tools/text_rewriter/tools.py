import docx
import PyPDF2
import csv
import os
from typing import Optional

def read_file(file_url: str, file_type: str) -> str:
    """
    Reads the input file and converts it to plain text.
    
    Parameters:
    - file_url (str): URL or path to the file.
    - file_type (str): Type of the file (csv, pdf, docx, etc.).
    
    Returns:
    - str: Extracted text from the file.
    """
    if file_type == "csv":
        return file_to_text_converter.read_csv(file_url)
    elif file_type == "pdf":
        return file_to_text_converter.read_pdf(file_url)
    elif file_type == "docx":
        return file_to_text_converter.read_docx(file_url)
    elif file_type == "txt":
        return file_to_text_converter.read_txt(file_url)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def rewrite_text(input_text: str, instructions: str) -> str:
    """
    Rewrites the input text according to the provided instructions.
    
    Parameters:
    - input_text (str): The text to be rewritten.
    - instructions (str): Instructions to guide the rewriting process.
    
    Returns:
    - str: The rewritten text.
    """
    # This is a placeholder for actual AI integration.
    # For now, it just returns the text with a note indicating it's rewritten.
    if "simplify the text for a middle school audience" in instructions.lower():
        # Simplify the text for middle school audience (very basic transformation)
        simplified_text = input_text.replace("tragic play", "sad play") \
                                    .replace("reconcile their feuding families", "bring peace to their fighting families") \
                                    .replace("lovers whose deaths ultimately reconcile", "two young people who fall in love but die in the end")
        return simplified_text
    else:
        # If no instruction matches, return original text
        return input_text
# Example of a helper module for file conversions
class file_to_text_converter:
    
    @staticmethod
    def read_csv(file_url: str) -> str:
        with open(file_url, mode='r') as file:
            reader = csv.reader(file)
            text = "\n".join([",".join(row) for row in reader])
        return text

    @staticmethod
    def read_pdf(file_url: str) -> str:
        with open(file_url, mode='rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text

    @staticmethod
    def read_docx(file_url: str) -> str:
        doc = docx.Document(file_url)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    @staticmethod
    def read_txt(file_url: str) -> str:
        with open(file_url, 'r') as file:
            text = file.read()
        return text

