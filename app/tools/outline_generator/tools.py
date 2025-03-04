from pydantic import BaseModel
from typing import List
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.logger import setup_logger
import os

logger = setup_logger(__name__)
def read_text_file(file_path):
    # Get the directory containing the script file
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Combine the script directory with the relative file path
        absolute_file_path = os.path.join(script_dir, file_path)
        
        with open(absolute_file_path, 'r') as file:
            return file.read()
class OutlineGeneratorPipeline:
    def __init__(self, args=None, verbose=False):
        self.verbose = verbose
        self.args = args
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore_class = Chroma
        #parsers is the format of the output required
        self.parser =JsonOutputParser(pydantic_object=Outline)
        self.prompt=read_text_file('./prompt/outline_generator_prompt.txt')
        self.vectorstore = None
        self.retriever = None

    def generate_outline(self):
        pipeline = self.compile_pipeline()
        inputs = {
            "text_context": self.args.text_context,
            "instructional_level": self.args.instructional_level,
            "no_of_slides": self.args.no_of_slides,     
        }

        results = pipeline.invoke(inputs)
        if self.verbose:
            logger.info("Lesson Plan successfully generated.")
        return results
    
   
        
    def compile_pipeline(self):
        prompt = PromptTemplate(          
                template=self.prompt,        
                input_variables=["instructional_level", "no_of_slides", "text_context"],           
                partial_variables={"format_instructions": self.parser.get_format_instructions()}        
                )
        chains =  prompt | self.model | self.parser
        return chains

class Outline(BaseModel):
    outlines:List[str]

