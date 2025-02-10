import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate

EVAL_PROMPT = PromptTemplate(
    input_variables=["source_documents", "quiz_questions"],
    template="""You are evaluating quiz questions based on source documents. Analyze the questions using the following criteria and provide numerical scores (1-5) for each:

    Source Documents:
    {source_documents}

    Quiz Questions:
    {quiz_questions}

    Please evaluate and score each criterion on a scale of 1-5 (where 1 is lowest and 5 is highest):

    1. Content Alignment (1-5):
    - How well do questions match the source content?
    - Are key concepts from documents represented?
    - Is the information accurate according to sources?

    2. Uniqueness (1-5):
    - Are questions distinct from each other?
    - Do they test different aspects of the content?
    - Is there any redundancy in concepts tested?

    3. Coverage (1-5):
    - How well are all documents represented?
    - Is there balanced coverage across documents?
    - Are important topics from each document included?

    Provide your evaluation in the following JSON format:
    {{
        "content_alignment": {{
            "score": <number 1-5>,
            "reasoning": "<detailed explanation>"
        }},
        "uniqueness": {{
            "score": <number 1-5>,
            "reasoning": "<detailed explanation>"
        }},
        "coverage": {{
            "score": <number 1-5>,
            "reasoning": "<detailed explanation>"
        }},
        "overall_feedback": "<general feedback and suggestions for improvement>"
    }}
    """
)

class QuizEvaluator:   
    def __init__(self, llm = None):
        self.llm = llm or ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        self.eval_chain = EVAL_PROMPT | self.llm | JsonOutputParser()

        
    def evaluate_quiz(self, source_documents: List[str], quiz_questions: List[Dict], run_id) -> Dict:
        """
        Evaluate quiz questions against source documents.
        
        Args:
            source_documents (List[str]): List of source documents
            quiz_questions (List[Dict]): List of questions with their answers
            
        Returns:
            Dict: Evaluation results with scores and reasoning
        """
        # Format documents and questions for evaluation
        formatted_docs = "\n\n--- Document {} ---\n{}".format
        documents_text = "\n".join(
            formatted_docs(i+1, doc) for i, doc in enumerate(source_documents)
        )
        
        formatted_questions = "\n\n--- Question {} ---\n{}".format
        questions_text = "\n".join(
            formatted_questions(i+1, str(q)) for i, q in enumerate(quiz_questions)
        )
        
        # Run evaluation
        evaluation = self.eval_chain.invoke({
                "source_documents": documents_text,
                "quiz_questions": questions_text
            },
            config={
                'run_id': run_id
            })
            
        # Calculate overall score
        scores = [
            evaluation["content_alignment"]["score"],
            evaluation["uniqueness"]["score"],
            evaluation["coverage"]["score"]
        ]
        evaluation["overall_score"] = round(sum(scores) / len(scores), 2)
        
        return evaluation
