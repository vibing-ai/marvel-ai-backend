from pydantic import BaseModel, Field
from typing import List, Optional
import os
from app.services.logger import setup_logger
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from google.cloud import vertexai
import vertexai.language_models as lm
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

logger = setup_logger(__name__)

def read_text_file(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_file_path = os.path.join(script_dir, file_path)
    with open(absolute_file_path, 'r') as file:
        return file.read()

class Slide(BaseModel):
    title: str = Field(..., description="The title of the slide")
    content: str = Field(..., description="The actual content of the slide")
    template: str = Field(default="titleBody", description="Slide template (e.g., titleBody, titleBullets, twoColumn)")

class FullPresentation(BaseModel):
    main_title: str = Field(..., description="The main title of the presentation")
    list_slides: List[Slide] = Field(..., description="The full collection of slides")

class PresentationGenerator:
    def __init__(self, args, vectorstore_class=Chroma, embedding_model=None, verbose=False):
        vertexai.init(project="marvelai-project", location="us-central1")
        self.model = lm.TextGenerationModel.from_pretrained("gemini-1.5-pro")
        self.parser = JsonOutputParser(pydantic_object=FullPresentation)
        self.prompt_outline = read_text_file("prompt/presentation-generator-outline.txt")
        self.prompt_slides = read_text_file("prompt/presentation-generator-slides.txt")
        self.embedding_model = embedding_model or GoogleGenerativeAIEmbeddings(model='models/embedding-001')
        self.vectorstore_class = vectorstore_class
        self.args = args
        self.verbose = verbose
        self.vectorstore = None

        # Validate PRD-required inputs
        if not args.text: raise ValueError("Topic must be provided")
        if not args.slideCount: raise ValueError("Number of slides must be provided")
        if int(args.slideCount) < 5 or int(args.slideCount) > 20:
            raise ValueError("Number of slides must be between 5 and 20")
        if not args.instructionalLevel: raise ValueError("Instructional level must be provided")

    def compile_with_context(self, documents: List[Document]):
        # Outline prompt with context
        outline_prompt = PromptTemplate(
            template=self.prompt_outline,
            input_variables=["text", "slideCount", "instructionalLevel", "objectives", "additional_comments", "context"],
            partial_variables={"format_instructions": JsonOutputParser(pydantic_object=list).get_format_instructions()}
        )
        slides_prompt = PromptTemplate(
            template=self.prompt_slides,
            input_variables=["outline", "instructionalLevel", "objectives", "additional_comments", "context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        # Create vectorstore and retriever
        if not self.vectorstore:
            logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            retriever = self.vectorstore.as_retriever()

        # Phase 1: Generate outline with context
        outline_chain = (
            RunnableParallel({
                "text": RunnablePassthrough(lambda x: x["text"]),
                "slideCount": RunnablePassthrough(lambda x: x["slideCount"]),
                "instructionalLevel": RunnablePassthrough(lambda x: x["instructionalLevel"]),
                "objectives": RunnablePassthrough(lambda x: x["objectives"]),
                "additional_comments": RunnablePassthrough(lambda x: x["additional_comments"]),
                "context": retriever
            })
            | outline_prompt
            | self.model
            | JsonOutputParser(pydantic_object=list)
        )

        # Phase 2: Generate slides with context
        slides_chain = (
            RunnableParallel({
                "outline": RunnablePassthrough(),
                "instructionalLevel": lambda x: self.args.instructionalLevel,
                "objectives": lambda x: self.args.objectives or "",
                "additional_comments": lambda x: self.args.additional_comments or "",
                "context": retriever
            })
            | slides_prompt
            | self.model
            | self.parser
        )

        return outline_chain | slides_chain

    def compile_without_context(self):
        outline_prompt = PromptTemplate(
            template=self.prompt_outline,
            input_variables=["text", "slideCount", "instructionalLevel", "objectives", "additional_comments"],
            partial_variables={"format_instructions": JsonOutputParser(pydantic_object=list).get_format_instructions()}
        )
        slides_prompt = PromptTemplate(
            template=self.prompt_slides,
            input_variables=["outline", "instructionalLevel", "objectives", "additional_comments"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        # Phase 1: Generate outline
        outline_chain = outline_prompt | self.model | JsonOutputParser(pydantic_object=list)

        # Phase 2: Generate slides
        slides_chain = (
            RunnableParallel({
                "outline": RunnablePassthrough(),
                "instructionalLevel": lambda x: self.args.instructionalLevel,
                "objectives": lambda x: self.args.objectives or "",
                "additional_comments": lambda x: self.args.additional_comments or ""
            })
            | slides_prompt
            | self.model
            | self.parser
        )

        return outline_chain | slides_chain

    def generate_presentation(self, documents: Optional[List[Document]] = None):
        logger.info("Creating the presentation")
        chain = self.compile_with_context(documents) if documents else self.compile_without_context()
        input_dict = {
            "text": self.args.text,
            "slideCount": self.args.slideCount,
            "instructionalLevel": self.args.instructionalLevel,
            "objectives": self.args.objectives or "",
            "additional_comments": self.args.additional_comments or ""
        }
        if documents:
            input_dict["context"] = "\n".join(doc.page_content for doc in documents)
        response = chain.invoke(input_dict)

        # Optional: Enforce template assignment consistency
        for slide in response["list_slides"]:
            slide["template"] = self.assign_template(slide["content"])

        logger.info(f"Generated response: {response}")
        if documents and self.vectorstore:
            if self.verbose: print("Deleting vectorstore")
            self.vectorstore.delete_collection()
        return response

    def assign_template(self, content: str) -> str:
        if "\n" in content or len(content.split()) < 50:
            return "titleBullets"
        elif len(content.split()) > 100:
            return "twoColumn"
        return "titleBody"
    
    # Optional: Enforce template assignment consistency
    # for slide in response["list_slides"]:
    # slide["template"] = self.assign_template(slide["content"])
