from typing import List, Dict
import os
from operator import itemgetter
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser, BaseOutputParser
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langsmith import traceable

from app.services.logger import setup_logger

relative_path = "tools/multiple_choice_quiz_generator"

logger = setup_logger(__name__)

def transform_json_dict(input_data: dict) -> dict:
    generated_questions = []

    # Validate and parse the input data to ensure it matches the QuizQuestion schema
    quiz_questions_list = QuizQuestionsList(**input_data)
    
    for question in quiz_questions_list.questions_list:
        transformed_question = {
                "question": question.question,
                "choices": {choice.key: choice.value for choice in question.choices},
                "answer": question.answer,
                "explanation": question.explanation
            }
        generated_questions.append(transformed_question)

    return generated_questions

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class QuizBuilderConfig:
    
    def __init__(
        self,
        model = None,
        embedding_model = None,
        vectorstore_class = None,
        max_questions: int = 10,
        min_questions: int = 1,
        max_attempts: int = 2,
        prompt_template_path: str = "prompt/multiple_choice_quiz_generator_prompt.txt",
        multi_query_prompt_path: str = "prompt/multi_query_prompt.txt",
        parser: JsonOutputParser = None,
        verbose: bool = False,
        score_threshold: float = 0.4
    ):
        self.model = model or GoogleGenerativeAI(model="gemini-1.5-pro", max_output_tokens=None ) 
        self.embedding_model = embedding_model or GoogleGenerativeAIEmbeddings(model='models/embedding-001')
        self.vectorstore_class = vectorstore_class or Chroma
        self.max_questions = max_questions
        self.min_questions = min_questions
        self.max_attempts = max_attempts
        self.prompt_template_path = prompt_template_path
        self.multi_query_prompt_path = multi_query_prompt_path
        self.verbose = verbose
        self.score_threshold = score_threshold

        # load the prompt template
        self.prompt_template = read_text_file(self.prompt_template_path)
        self.multi_query_prompt_template = read_text_file(self.multi_query_prompt_path)

        self.parser = parser or JsonOutputParser(pydantic_object=QuizQuestionsList)

class QuizBuilder:
            
    def __init__(
        self, 
        topic: str, 
        n_questions: int, 
        grade_level: str, 
        quiz_description: str = "", 
        lang: str ='en', 
        config: QuizBuilderConfig = None, 
        verbose: bool = False
    ):
        """
            Initialize the QuizBuilder with configuration and models.
            
            Args:
                topic (str): The main topic for quiz questions
                n_questions (int): The number of questions to generate
                grade_level (str): The grade level for the quiz
                quiz_description (str): Description of the quiz (default: "")
                lang (str): Language code for question generation (default: 'en')
                config (QuizBuilderConfig): Configuration object for the quiz builder (default: None)   
                verbose (bool): Enable detailed logging (default: False)
        """
        self.topic = topic
        self.lang = lang
        self.n_questions = n_questions
        self.grade_level = grade_level
        self.quiz_description = quiz_description

        self.config = config or QuizBuilderConfig(verbose=verbose)
        self.verbose = verbose
        self.runner = None
        self._model = self.config.model
        self._prompt_template = self.config.prompt_template
        self._parser = self.config.parser

        # Initialize components
        self.vectorstore_manager = VectorStoreManager(self.config)
        self.retriever_factory = RetrieverFactory(self.config)

        if topic is None: raise ValueError("Topic must be provided")

    def get_optional_instructions(self, input_name: str, input_value: str) -> str:
        """
        Get the optional instructions for a given input variable.
        
        Args:
            input_name (str): The name of the input variable
            input_value (str): The value of the input variable
        
        Returns:
            str: The optional instructions for the input variable
        """
        OPT_INSTRUCTIONS_TEMPLATE = {
            "quiz_description": "- Assessment Description: %s"
        }
        if input_name in OPT_INSTRUCTIONS_TEMPLATE:
            return OPT_INSTRUCTIONS_TEMPLATE[input_name] % input_value
        else:
            return ""
    
    def compile(self, documents: List[Document]) -> RunnableParallel:
        """
        Compile the question generation chain using the provided documents.
        
        Args:
            documents (List[Document]): List of documents to use as context
            
        Returns:
            Chain: A compiled LangChain chain for question generation
        """
        # Initialize prompt template with all required variables
        prompt = PromptTemplate(
            template=self._prompt_template,
            input_variables=["topic", "lan", "context", "num_questions", "grade_level", "quiz_description"],
            partial_variables={"format_instructions": self._parser.get_format_instructions()})

        number_documents = len(documents)

        # Create vector store and retriever if not already initialized
        if self.runner is None:
            vectorstore = self.vectorstore_manager.create_vectorstore(documents)
            retriever_k = number_documents # Set the retriever k value to the number of documents
            retriever = self.retriever_factory.create_multiquery_retriever(
                vectorstore, 
                self.n_questions, 
                retriever_k
            )

            # Set up parallel running to pass all required variables for prompt
            self.runner = RunnableParallel(
                {
                    "context": itemgetter("topic") |  retriever, # Retrieves relevant context from documents
                    "topic": itemgetter("topic"),  # Passes through the topic
                    "lang": itemgetter("lang"),  # Passes through the language
                    "num_questions": itemgetter("n_questions"),  # Passes through the number of questions
                    "grade_level": itemgetter("grade_level"),  # Passes through the grade level
                    "quiz_description": 
                        lambda input : self.get_optional_instructions(
                            "quiz_description", 
                            input["quiz_description"])  # Passes through the quiz description
                }
            )
        logger.info(f"Runner initialized") if self.verbose else None

        # Compile the full chain: runner -> prompt -> model -> parser
        chain = (self.runner | prompt | self._model | self._parser)
        
        logger.info(f"Chain compilation complete") if self.verbose else None
        
        return chain

    def create_questions(self, documents: List[Document]) -> List[Dict]:
        """
        Generate multiple-choice quiz questions based on the provided documents.
        
        Args:
            documents (List[Document]): List of documents to use as context
            
        Returns:
            List[Dict]: List of generated quiz questions with choices and answers
        """
        logger.info(f"Creating {self.n_questions} questions") if self.verbose else None
     
        if self.n_questions > self.config.max_questions:
            return {"message": "error", "data": f"Number of questions cannot exceed {self.config.max_questions}"}
        
        try:
            chain = self.compile(documents)

            user_input = {
                "n_questions": self.n_questions,
                "topic": self.topic,
                "lang": self.lang,
                "grade_level": self.grade_level,
                "quiz_description": self.quiz_description
            }
            generated_questions = self.run_chain(chain, user_input)

            number_gen_questions = len(generated_questions)
            logger.info(f"Total generated questions: {number_gen_questions}") if self.verbose else None
            
            # Log if fewer questions are generated
            if number_gen_questions < self.n_questions:
                if self.verbose: 
                    logger.warning(f"Only generated {number_gen_questions} out of "
                                   "{self.n_questions} requested questions")
            
            # Return requested number of questions (or fewer if not enough were generated)
            return generated_questions[:self.n_questions]
        except Exception as e:
            if self.verbose:
                logger.error(f"Error generating questions: {e}")
            raise e
        finally:
            self.cleanup()

    
    def run_chain(self, chain: RunnableParallel, user_input: dict) -> List[Dict]:
        """
        Run the LangChain pipeline to generate quiz questions.

        Args:
            chain (RunnableParallel): The compiled LangChain pipeline
            user_input (dict): The input data for the pipeline
        """
        generated_questions = []
        attempts = 0
        max_attempts = self.config.max_attempts  # Allow for more attempts to generate questions

        while not generated_questions and attempts < max_attempts:
            error = None
            if self.verbose:
                logger.info(f"Running pipeline. Attempt {attempts + 1} of {max_attempts}")

            try:
                # Run the pipeline with the provided input data
                response = chain.invoke(user_input)
        
                logger.info(f"Generated response: {response}") if self.verbose else None

                questions_list = transform_json_dict(response)
                for question in questions_list:
                    # Directly check if the response format is valid
                    if self.validate_response(question):
                        question["choices"] = self.format_choices(question["choices"])
                        generated_questions.append(question)
                        if self.verbose:
                            logger.info(f"Valid question added: {question}")
                    else:
                        if self.verbose:
                            logger.warning(f"Invalid response format. Attempt {attempts + 1} of {max_attempts}")
            except TypeError as e:
                error = f"TypeError generating questions: {e}"
                if self.verbose:
                    logger.error(error)
            except Exception as e:
                error = f"Error generating questions: {e}"
                if self.verbose:
                    logger.error(error)
            finally:
                if error:
                    generated_questions = []
                attempts += 1

        if error: 
            raise Exception(error)
            
        return generated_questions

    
    #new function to validate the response
    def validate_response(self, response: dict) -> bool:
        """
        Validates the structure and content of a quiz question response.
        
        Args:
            response (dict): The quiz question response to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check if all required fields are present
            required_fields = ['question', 'choices', 'answer', 'explanation']
            if not all(field in response for field in required_fields):
                logger.warning("Missing required fields") if self.verbose else None
                return False
            
            # Validate choices
            if not isinstance(response['choices'], dict):
                logger.warning("Choices must be a dictionary") if self.verbose else None
                return False
            
            # Validate that there are exactly 4 choices
            if len(response['choices']) != 4:
                logger.warning("Must have exactly 4 choices") if self.verbose else None
                return False
            
            # Validate choice keys are A, B, C, D
            valid_keys = set(['A', 'B', 'C', 'D'])
            if set(response['choices'].keys()) != valid_keys:
                logger.warning("Choice keys must be A, B, C, D") if self.verbose else None
                return False
            
            # Validate answer is one of the valid keys
            if response['answer'] not in valid_keys:
                logger.warning("Answer must be one of: A, B, C, D") if self.verbose else None
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}") if self.verbose else None
            return False

    def format_choices(self, choices: dict) -> dict:
        """
        Formats the choices to ensure they are in the correct order and structure.
        
        Args:
            choices (dict): Dictionary of choices with keys A, B, C, D
            
        Returns:
            dict: Formatted choices in correct order
        """
        ordered_keys = ['A', 'B', 'C', 'D']
        return {key: choices[key] for key in ordered_keys if key in choices}
    
    def vote_question(self, question_index: int, vote_type: str) -> bool:
        """
        Add a vote to a specific question
        
        Args:
            question_index (int): Index of the question
            vote_type (str): Either 'up' or 'down'
            
        Returns:
            bool: True if vote was successful
        """
        try:
            if vote_type == 'up':
                self.questions[question_index].thumbs_up += 1
            elif vote_type == 'down':
                self.questions[question_index].thumbs_down += 1
            return True
        except (IndexError, AttributeError):
            return False

    def cleanup(self):
        """
        Cleanup resources used by the QuizBuilder.
        """
        if self.verbose:
            logger.info("Cleaning up resources")

        self.vectorstore_manager.cleanup()
        self.vectorstore_manager = None
        self.retriever_factory.cleanup()
        self.retriever_factory = None

class RetrieverFactory:
    
    def __init__(self, config: QuizBuilderConfig):
        self.verbose = config.verbose

        self._model = config.model
        self._prompt_template = config.multi_query_prompt_template
        self._score_threshold = config.score_threshold
    
    def create_multiquery_prompt(self, num_questions: int) -> PromptTemplate:
        try:
            return PromptTemplate(
                input_variables=["question"],
                partial_variables={
                    "num_questions": num_questions,
                },
                template=self._prompt_template
            )
        except Exception as e:
            logger.error(f"Failed to create multiquery prompt: {e}") if self.verbose else None
            raise Exception(f"Prompt creation failed: {str(e)}")

    def create_base_retriever(self, vectorstore, retriever_k: int, score_threshold: float):
        try:
            return vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": retriever_k,
                    "score_threshold": score_threshold
                }
            )
        except Exception as e:
            logger.error(f"Failed to create base retriever: {e}")
            raise Exception(f"Base retriever creation failed: {str(e)}")

    def create_multiquery_chain(self, prompt: PromptTemplate):
        # Create the multiquery chain
        try:
            output_parser = QueryListOutputParser()
            return prompt | self._model | output_parser
        except Exception as e:
            logger.error(f"Failed to create multiquery chain: {e}")
            raise Exception(f"Chain creation failed: {str(e)}")

    def create_multiquery_retriever(
        self, 
        vectorstore,
        num_questions: int,
        retriever_k: int,
        score_threshold: float = None,
        only_page_content: bool = True
    ) -> MultiQueryRetriever:
        if self.verbose:
            logger.info("Setting up MultiQueryRetriever")
            
        try:
            search_score_threshold = score_threshold or self._score_threshold
            base_retriever = self.create_base_retriever(vectorstore, retriever_k, search_score_threshold)
            prompt = self.create_multiquery_prompt(num_questions)
            chain = self.create_multiquery_chain(prompt)
            
            retriever = MultiQueryRetriever(
                retriever=base_retriever,
                llm_chain=chain,
                parser_key="lines",
                verbose=self.verbose
            )
            
            if self.verbose:
                logger.info("MultiQueryRetriever created successfully")
            
            factory = self
            def wrapper_retriever(inputs):
                if self.verbose:
                    logger.info(f"Invoking enhanced retriever with inputs: {inputs}")

                retrieved_docs = retriever.invoke(inputs)
                factory.number_retrieved_docs = len(retrieved_docs)

                if self.verbose:
                    logger.info(f"Retrieved {factory.number_retrieved_docs} documents")

                if only_page_content:
                    if self.verbose:
                        logger.info("Returning only page content")
                    return [doc.page_content for doc in retrieved_docs]
                
                return retrieved_docs

            return RunnableLambda(wrapper_retriever)
            
        except Exception as e:
            logger.error(f"Failed to create enhanced retriever: {e}")
            raise Exception(f"Multiquery retriever creation failed: {str(e)}")
        
    def cleanup(self):
        """
        Cleanup resources used by the RetrieverFactory.
        """
        if self.verbose:
            logger.info("Cleaning up RetrieverFactory resources")
        self._model = None
        
class VectorStoreManager:
    
    def __init__(self, config: QuizBuilderConfig):
        self.config = config
        self.verbose = config.verbose
        self._vectorstore_class = self.config.vectorstore_class
        self._embedding_model = self.config.embedding_model 
        
        self._vectorstore = None
    
    @property
    def vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = self.create_vectorstore()
        return self._vectorstore
    
    @traceable(run_type="embedding")
    def create_vectorstore(self, documents: List[Document]):

        logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
        self._vectorstore = self._vectorstore_class.from_documents(
            documents, 
            self._embedding_model
        )
        logger.info(f"Vectorstore created") if self.verbose else None
        return self._vectorstore
    
    def cleanup(self):
        if self.verbose: logger.info(f"Deleting vectorstore")
        if self._vectorstore:
            self._vectorstore.delete_collection()
            self._vectorstore = None
            self._vectorstore_class = None

class QueryListOutputParser(BaseOutputParser[List[str]]):
    # Output parser for a list of lines.
    def parse(self, text: str) -> List[str]:
        lines = text.strip().split("\n")
        return list(filter(None, lines)) 
    
class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")

class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")
    explanation: str = Field(description="An explanation of why the answer is correct")
    thumbs_up: int = Field(default=0, description="Number of thumbs up votes")
    thumbs_down: int = Field(default=0, description="Number of thumbs down votes")

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
                ]

          """
        }

      }
    

