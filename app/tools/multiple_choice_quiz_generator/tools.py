from typing import List, Dict
import os

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.globals import set_debug


from langchain.chains.combine_documents import create_stuff_documents_chain

from app.services.logger import setup_logger

relative_path = "tools/multiple_choice_quiz_generator"

logger = setup_logger(__name__)

set_debug(True)

def transform_json_dict(input_data: dict) -> dict:
    generated_questions = []

    # Validate and parse the input data to ensure it matches the QuizQuestion schema

    quiz_questions_list = QuizQuestionsList(**input_data)
    # quiz_question = QuizQuestion(**input_data)
    for question in quiz_questions_list.questions_list:
        transformed_question = {
                "question": question.question,
                "choices": {choice.key: choice.value for choice in question.choices},
                "answer": question.answer,
                "explanation": question.explanation
            }
        generated_questions.append(transformed_question)

    return generated_questions

#safely and robustly read the contents of a text file, while also handling potential errors gracefully
def read_text_file(file_path):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_file_path = os.path.join(script_dir, file_path)
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

class QuizBuilder:
    def __init__(self, topic, lang='en', vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-pro", max_output_tokens=None ),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=QuizQuestionsList),
            "prompt": read_text_file("prompt/multiple_choice_quiz_generator_prompt.txt"),
            "vectorstore_class": Chroma
        }
        
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.topic = topic
        self.lang = lang
        self.verbose = verbose
        
        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if topic is None: raise ValueError("Topic must be provided")
    
    def compile(self, documents: List[Document], num_questions):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions(), 
                               "num_questions": num_questions}
        )

        # if self.runner is None:
            # logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            # self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            # logger.info(f"Vectorstore created") if self.verbose else None

            # self.retriever = self.vectorstore.as_retriever()
            # logger.info(f"Retriever created successfully") if self.verbose else None

            
            # self.runner = RunnableParallel(
            #     {
            #     "context": self.retriever, 
            #     "attribute_collection": RunnablePassthrough()
            #     }
            # )
        
        # chain = self.runner | prompt | self.model | self.parser
        chain = create_stuff_documents_chain(self.model, prompt, output_parser=self.parser)
        
        if self.verbose: logger.info(f"Chain compilation complete")
        
        return chain

    def validate_response(self, response: Dict) -> bool:
        try:
            # Assuming the response is already a dictionary
            if isinstance(response, dict):
                if 'question' in response and 'choices' in response and 'answer' in response and 'explanation' in response:
                    choices = response['choices']
                    if isinstance(choices, dict):
                        for key, value in choices.items():
                            if not isinstance(key, str) or not isinstance(value, str):
                                return False
                        return True
            return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False

    def format_choices(self, choices: Dict[str, str]) -> List[Dict[str, str]]:
        return [{"key": k, "value": v} for k, v in choices.items()]
    
    def create_questions(self, documents: List[Document], num_questions: int = 5) -> List[Dict]:
        if self.verbose: logger.info(f"Creating {num_questions} questions")
     
        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}
        
        chain = self.compile(documents, num_questions)
        
        generated_questions = []
        attempts = 0
        max_attempts = num_questions * 5  # Allow for more attempts to generate questions ???

        # Run the pipeline with the provided input data
        # response = chain.invoke(f"Topic: {self.topic}, Lang: {self.lang}")
        response = chain.invoke({"attribute_collection": f"Topic: {self.topic}, Lang: {self.lang}",
                                 "context": documents})
        logger.info(f"Generated response: {response}")

        questions_list = transform_json_dict(response)
        for question in questions_list:
            # Directly check if the response format is valid
            if self.validate_response(question):
                question["choices"] = self.format_choices(question["choices"])
                generated_questions.append(question)
                if self.verbose:
                    logger.info(f"Valid question added: {question}")
                    logger.info(f"Total generated questions: {len(generated_questions)}")
            else:
                if self.verbose:
                    logger.warning(f"Invalid response format. Attempt {attempts + 1} of {max_attempts}")

        # Log if fewer questions are generated
        if len(generated_questions) < num_questions:
            if self.verbose: logger.warning(f"Only generated {len(generated_questions)} out of {num_questions} requested questions")
        
        if self.verbose: logger.info(f"Deleting vectorstore")
        # self.vectorstore.delete_collection()
        
        # Return the list of questions
        return generated_questions[:num_questions]

class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")

class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")
    explanation: str = Field(description="An explanation of why the answer is correct")

class QuizQuestionsList(BaseModel):
    questions_list: List[QuizQuestion] = Field(description="A list of questions for the quiz")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                "questions_list": [
                    {
                        "question": "What is the capital of France?",
                        "choices": [
                            {"key": "A", "value": "Berlin"},
                            {"key": "B", "value": "Madrid"},
                            {"key": "C", "value": "Paris"},
                            {"key": "D", "value": "Rome"},
                        ],
                        "answer": "C",
                        "explanation": "Paris is the capital of France."
                    },
                    {
                        "question": "What is the official language of France?",
                        "choices": [
                            {"key": "A", "value": "French"},
                            {"key": "B", "value": "English"},
                            {"key": "C", "value": "German"},
                            {"key": "D", "value": "Spanish"}
                        ],
                        "answer": "A",
                        "explanation": "The official language of France is French."
                    },
                ]§

          """
        }

      }
    

