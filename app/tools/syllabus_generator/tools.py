from pydantic import BaseModel, Field
from typing import List, Dict
from app.services.logger import setup_logger
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain.chains import SequentialChain
from app.services.schemas import SyllabusGeneratorArgsModel
from fastapi import HTTPException

logger = setup_logger(__name__)

class SyllabusRequestArgs:
    def __init__(self, syllabus_generator_args: SyllabusGeneratorArgsModel, summary: str):
        self._grade_level = syllabus_generator_args.grade_level
        self._subject = syllabus_generator_args.subject
        self._course_description = syllabus_generator_args.course_description
        self._objectives = syllabus_generator_args.objectives
        self._required_materials = syllabus_generator_args.required_materials
        self._grading_policy = syllabus_generator_args.grading_policy
        self._policies_expectations = syllabus_generator_args.policies_expectations
        self._course_outline = syllabus_generator_args.course_outline
        self._additional_notes = syllabus_generator_args.additional_notes
        self._lang = syllabus_generator_args.lang
        self._summary = summary
        self._unit_time = syllabus_generator_args.unit_time
        self._unit_time_value = syllabus_generator_args.unit_time_value
        self._start_date = syllabus_generator_args.start_date

    def to_dict(self) -> dict:
        return {
            "grade_level": self._grade_level,
            "subject": self._subject,
            "course_description": self._course_description,
            "objectives": self._objectives,
            "required_materials": self._required_materials,
            "grading_policy": self._grading_policy,
            "policies_expectations": self._policies_expectations,
            "course_outline": self._course_outline,
            "additional_notes": self._additional_notes,
            "lang": self._lang,
            "summary": self._summary,
            "unit_time": self._unit_time,
            "unit_time_value": self._unit_time_value,
            "start_date": self._start_date
        }

class SyllabusGeneratorPipeline:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")

    def compile(self):
        # Sequential prompts with enhanced templates
        course_info_prompt = PromptTemplate(
            template=(
                "Generate a structured course overview for {grade_level} {subject} in {lang}.\n"
                "Include:\n- A brief course description based on: {course_description}\n"
                "- Core topics derived from: {course_outline}\n"
                "- Target learners (e.g., age group, prior knowledge) for {grade_level}.\n"
                "Respond as a JSON object."
            ),
            input_variables=["grade_level", "subject", "course_description", "course_outline", "lang"]
        )

        learning_outcomes_prompt = PromptTemplate(
            template=(
                "Based on this course information: {course_info}, create 5-7 key learning outcomes "
                "in {lang} that students should achieve by the end of the course. Make them specific, "
                "measurable, and aligned with the course description and core topics.\n"
                "Respond as a JSON object."
            ),
            input_variables=["course_info", "lang"]
        )

        course_content_prompt = PromptTemplate(
            template=(
                "Using these learning outcomes: {learning_outcomes}, generate a structured course plan "
                "in {lang} for {unit_time_value} {unit_time}s. Include topics, subtopics, and estimated "
                "time allocation for each, ensuring alignment with the outcomes.\n"
                "Respond as a JSON object."
            ),
            input_variables=["learning_outcomes", "unit_time", "unit_time_value", "lang"]
        )

        assessment_criteria_prompt = PromptTemplate(
            template=(
                "Given this course content: {course_content}, develop a fair and balanced grading policy "
                "in {lang}. Include different assessment types (e.g., homework, quizzes, exams) and their "
                "respective weightage, ensuring they align with the course structure.\n"
                "Respond as a JSON object."
            ),
            input_variables=["course_content", "lang"]
        )

        course_schedule_prompt = PromptTemplate(
            template=(
                "Using this course content: {course_content} and assessment criteria: {assessment_criteria}, "
                "create a detailed course schedule in {lang} starting on {start_date} for {unit_time_value} "
                "{unit_time}s. Ensure assessments align with learning progression and include specific dates.\n"
                "Respond as a JSON object."
            ),
            input_variables=["course_content", "assessment_criteria", "start_date", "unit_time", "unit_time_value", "lang"]
        )

        # Parallel prompts (independent sections)
        learning_resources_prompt = PromptTemplate(
            template=(
                "Suggest relevant learning resources (textbooks, websites, articles, etc.) in {lang} "
                "for a {grade_level} {subject} course based on: {required_materials} and {summary}.\n"
                "Respond as a JSON object."
            ),
            input_variables=["grade_level", "subject", "required_materials", "summary", "lang"]
        )

        policies_procedures_prompt = PromptTemplate(
            template=(
                "Outline course policies and procedures in {lang}, including attendance, late submissions, "
                "academic integrity, and classroom conduct, based on: {policies_expectations} and {course_info}.\n"
                "Respond as a JSON object."
            ),
            input_variables=["policies_expectations", "course_info", "lang"]
        )

        # Sequential chain
        course_info_chain = course_info_prompt | self.model
        learning_outcomes_chain = learning_outcomes_prompt | self.model
        course_content_chain = course_content_prompt | self.model
        assessment_criteria_chain = assessment_criteria_prompt | self.model
        course_schedule_chain = course_schedule_prompt | self.model

        sequential_chain = SequentialChain(
            chains=[
                course_info_chain,
                learning_outcomes_chain,
                course_content_chain,
                assessment_criteria_chain,
                course_schedule_chain
            ],
            input_variables=["grade_level", "subject", "course_description", "course_outline", "lang", 
                            "unit_time", "unit_time_value", "start_date"],
            output_variables=["course_info", "learning_outcomes", "course_content", 
                            "assessment_criteria", "course_schedule"]
        )

        # Parallel chain
        parallel_chain = RunnableParallel(
            learning_resources=learning_resources_prompt | self.model,
            policies_procedures=policies_procedures_prompt | self.model
        )

        hybrid_pipeline = {
            "sequential": sequential_chain,
            "parallel": parallel_chain
        }

        if self.verbose:
            logger.info("Compiled enhanced hybrid syllabus generation pipeline.")
        return hybrid_pipeline

def generate_syllabus(request_args: SyllabusRequestArgs, verbose=True):
    try:
        pipeline = SyllabusGeneratorPipeline(verbose=verbose)
        hybrid_chain = pipeline.compile()
        
        inputs = request_args.to_dict()
        sequential_output = hybrid_chain["sequential"].invoke(inputs)
        parallel_output = hybrid_chain["parallel"].invoke(inputs)

        syllabus = {
            "course_information": sequential_output["course_info"],
            "learning_outcomes": sequential_output["learning_outcomes"],
            "course_content": sequential_output["course_content"],
            "assessment_criteria": sequential_output["assessment_criteria"],
            "course_schedule": sequential_output["course_schedule"],
            "learning_resources": parallel_output["learning_resources"],
            "policies_procedures": parallel_output["policies_procedures"]
        }
        
        return syllabus

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {e}")
        raise HTTPException(status_code=500, detail="Syllabus generation failed.")