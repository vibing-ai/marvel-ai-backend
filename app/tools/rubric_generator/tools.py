from pydantic import BaseModel, Field
from typing import List, Dict
import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.logger import setup_logger
from app.tools.utils.tool_utilities import read_text_file

logger = setup_logger(__name__)

class RubricGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=RubricOutput),
            "prompt": read_text_file("prompt/rubric-generator-prompt.txt"),
            "prompt_without_context": read_text_file("prompt/rubric-generator-without-context-prompt.txt"),
            "vectorstore_class": Chroma
        }

        self.prompt = prompt or default_config["prompt"]
        self.prompt_without_context = default_config["prompt_without_context"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose

        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if args.grade_level is None: raise ValueError("Grade Level must be provided")
        if args.point_scale is None: raise ValueError("Point Scale must be provided")
        if int(args.point_scale) < 2 or int(args.point_scale) > 8:
            raise ValueError("Point Scale must be between 2 and 8. Suggested value is 4 for optimal granularity in grading.")
        if args.objectives is None: raise ValueError("Objectives description must be provided")
        if args.assignment_description is None: raise ValueError("Assignment description must be provided")
        if args.lang is None: raise ValueError("Language must be provided")

    def compile_with_context(self, documents: List[Document]):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        if self.runner is None:
            logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            logger.info(f"Vectorstore created") if self.verbose else None

            self.retriever = self.vectorstore.as_retriever()
            logger.info(f"Retriever created successfully") if self.verbose else None

            self.runner = RunnableParallel(
                {"context": self.retriever,
                "attribute_collection": RunnablePassthrough()
                }
            )

        chain = self.runner | prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain
    
    def compile_without_context(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt_without_context,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain

    def create_rubric(self, documents: List[Document]):
        logger.info(f"Creating the Rubric")

        if documents:
            chain = self.compile_with_context(documents)
        else:
            chain = self.compile_without_context()

         # Log the input parameters
        input_parameters = (
            f"Grade Level: {self.args.grade_level}, "
            f"Point Scale: {self.args.point_scale}, "
            f"Objectives: {self.args.objectives}, "
            f"Assignment Description: {self.args.assignment_description}, "
            f"Language (YOU MUST RESPOND IN THIS LANGUAGE): {self.args.lang}"
        )
        logger.info(f"Input parameters: {input_parameters}")

        attempt = 1
        max_attempt = 6

        while attempt < max_attempt:
            try:
                response = chain.invoke(input_parameters)
                logger.info(f"Rubric generated during attempt nb: {attempt}")
            except Exception as e:
                logger.error(f"Error during rubric generation: {str(e)}")
                attempt += 1
                continue
            if response == None:
                logger.error(f"could not generate Rubric, trying again")
                attempt += 1
                continue

            if self.validate_rubric(response) == False:
                attempt += 1
                continue

            # If everything is valid, break the outer loop
            break

        if attempt >= max_attempt:
            raise ValueError("Error: Unable to generate the Rubric after 5 attempts.")
        else:
            logger.info(f"Rubric successfully generated after {attempt} attempt(s).")

        if documents:
            if self.verbose: print(f"Deleting vectorstore")
            self.vectorstore.delete_collection()

        return response 
    
    def validate_rubric(self, response: Dict) -> bool:
         # Check if "criterias" exist and are valid
        if "criterias" not in response or len(response["criterias"]) == 0:
            logger.error("Rubric generation failed, criterias not created successfully, trying agian.")
            return False

        if "feedback" not in response:
            logger.error("Rubric generation failed, feedback not created successfully, trying again.")
            return False

        # Validate each criterion
        criteria_valid = True
        for criterion in response["criterias"]:
            if "criteria_description" not in criterion or len(criterion["criteria_description"]) != int(self.args.point_scale):
                logger.error("Mismatch between point scale nb and a criteria description. Trying again.")
                criteria_valid = False
                break  # Exit the for loop if a criterion is invalid

        if not criteria_valid:
            return False
        
        return True
    
class CriteriaDescription(BaseModel):
    points: str = Field(..., description="The total points gained by the student according to the point_scale an the level name")
    description: List[str] = Field(..., description="Description for the specific point on the scale")

class RubricCriteria(BaseModel):
    criteria: str = Field(..., description="name of the criteria in the rubric")
    criteria_description: List[CriteriaDescription] = Field(..., description="Descriptions for each point on the scale")
    
class RubricOutput(BaseModel):
    title: str = Field(..., description="the rubric title of the assignment based on the standard input parameter")
    grade_level: str = Field(..., description="The grade level for which the rubric is created")
    criterias: List[RubricCriteria] = Field(..., description="The grading criteria for the rubric")
    feedback: str = Field(..., description="the feedback provided by the AI model on the generated rubric")
