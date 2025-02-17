
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.logger import setup_logger
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os

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
        text_to_rewrite = docs[0].page_content if docs else self.args.text
        
        response = self.llm.invoke(
            [HumanMessage(content=self._create_prompt(text_to_rewrite, self.args.rewrite_style))]
        )
        
        # Parse the response to extract rewritten text and explanation
        response_parts = response.content.split('\n\n')
        rewritten_text = response_parts[0]
        explanation = response_parts[-1] if len(response_parts) > 1 else "Changes made to match requested style"
        
        return RewrittenText(
            original=text_to_rewrite,
            rewritten=rewritten_text,
            style=self.args.rewrite_style,
            changes_explained=explanation
        )
