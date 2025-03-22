from pydantic import BaseModel, Field
from typing import List, Dict
from app.services.logger import setup_logger
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
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
        }

class SyllabusGeneratorPipeline:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.parsers = {
            "course_information": JsonOutputParser(pydantic_object=CourseInformation),
            "course_description_objectives": JsonOutputParser(pydantic_object=CourseDescriptionObjectives),
            "course_content": JsonOutputParser(pydantic_object=CourseContentItem),
            "policies_procedures": JsonOutputParser(pydantic_object=PoliciesProcedures),
            "assessment_grading_criteria": JsonOutputParser(pydantic_object=AssessmentGradingCriteria),
            "learning_resources": JsonOutputParser(pydantic_object=LearningResource),
            "course_schedule": JsonOutputParser(pydantic_object=CourseScheduleItem),
        }

    def compile(self):
        try:
            prompts = {
                "course_information": PromptTemplate(
                    template=(
                        "Generate a detailed and structured course information in {lang} based on:\n\n"
                        "Grade Level: {grade_level}\n"
                        "Subject: {subject}\n"
                        "Course Description: {course_description}\n"
                        "Summary: {summary}\n\n"
                        "Ensure the response is professional and comprehensive.\n{format_instructions}"
                    ),
                    input_variables=["grade_level", "subject", "course_description", "lang", "summary"],
                    partial_variables={"format_instructions": self.parsers["course_information"].get_format_instructions()},
                ),
                "course_description_objectives": PromptTemplate(
                    template=(
                        "Develop detailed course objectives and intended learning outcomes in {lang}:\n\n"
                        "Objectives: {objectives}\n"
                        "Summary: {summary}\n\n"
                        "Provide measurable goals and realistic expectations for students.\n{format_instructions}"
                    ),
                    input_variables=["objectives", "lang", "summary"],
                    partial_variables={"format_instructions": self.parsers["course_description_objectives"].get_format_instructions()},
                ),
                "course_content": PromptTemplate(
                    template=(
                        "Create a detailed course content structure in {lang}:\n\n"
                        "Course Outline: {course_outline}\n"
                        "Summary: {summary}\n\n"
                        "Include topics, time frames, and key learning points.\n{format_instructions}"
                    ),
                    input_variables=["course_outline", "lang", "summary"],
                    partial_variables={"format_instructions": self.parsers["course_content"].get_format_instructions()},
                ),
                "policies_procedures": PromptTemplate(
                    template=(
                        "Draft clear and professional course policies and procedures in {lang}:\n\n"
                        "Grading Policy: {grading_policy}\n"
                        "Class Policies and Expectations: {policies_expectations}\n"
                        "Summary: {summary}\n\n"
                        "Ensure all rules and expectations are outlined clearly.\n{format_instructions}"
                    ),
                    input_variables=["grading_policy", "policies_expectations", "lang", "summary"],
                    partial_variables={"format_instructions": self.parsers["policies_procedures"].get_format_instructions()},
                ),
                "assessment_grading_criteria": PromptTemplate(
                    template=(
                        "Define assessment methods and grading criteria in {lang}:\n\n"
                        "Grading Policy: {grading_policy}\n"
                        "Summary: {summary}\n\n"
                        "Ensure that assessment methods and the grading scale are precise and easy to understand.\n{format_instructions}"
                    ),
                    input_variables=["grading_policy", "lang", "summary"],
                    partial_variables={"format_instructions": self.parsers["assessment_grading_criteria"].get_format_instructions()},
                ),
                "learning_resources": PromptTemplate(
                    template=(
                        "Generate a comprehensive list of recommended learning resources in {lang}:\n\n"
                        "Required Materials: {required_materials}\n"
                        "Summary: {summary}\n\n"
                        "Include titles, authors, and publication years of the materials.\n{format_instructions}"
                    ),
                    input_variables=["required_materials", "lang", "summary"],
                    partial_variables={"format_instructions": self.parsers["learning_resources"].get_format_instructions()},
                ),
                "course_schedule": PromptTemplate(
                    template=(
                        "Construct a detailed course schedule in {lang}:\n\n"
                        "Course Outline: {course_outline}\n"
                        "Summary: {summary}\n\n"
                        "Ensure the schedule includes dates, activities, and key topics.\n{format_instructions}"
                    ),
                    input_variables=["course_outline", "lang", "summary"],
                    partial_variables={"format_instructions": self.parsers["course_schedule"].get_format_instructions()},
                ),
            }

            chains = {
                key: prompt | self.model | self.parsers[key]
                for key, prompt in prompts.items()
            }

            parallel_pipeline = RunnableParallel(branches=chains)

            if self.verbose:
                logger.info("Successfully compiled the parallel pipeline.")

        except Exception as e:
            logger.error(f"Failed to compile LLM pipeline: {e}")
            raise HTTPException(status_code=500, detail="Failed to compile LLM pipeline.")

        return parallel_pipeline

def generate_syllabus(request_args: SyllabusRequestArgs, verbose=True):
    try:
        pipeline = SyllabusGeneratorPipeline(verbose=verbose)
        chain = pipeline.compile()
        outputs = chain.invoke(request_args.to_dict())
        model = SyllabusSchema(
            course_information=outputs["branches"]["course_information"],
            course_description_objectives=outputs["branches"]["course_description_objectives"],
            course_content=outputs["branches"]["course_content"],
            policies_procedures=outputs["branches"]["policies_procedures"],
            assessment_grading_criteria=outputs["branches"]["assessment_grading_criteria"],
            learning_resources=outputs["branches"]["learning_resources"],
            course_schedule=outputs["branches"]["course_schedule"],
        )
        return dict(model)

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate syllabus from LLM.")


class CourseInformation(BaseModel):
    course_title: str = Field(description="The course title")
    grade_level: str = Field(description="The grade level")
    description: str = Field(description="The course description")

class CourseDescriptionObjectives(BaseModel):
    objectives: List[str] = Field(description="The course objectives")
    intended_learning_outcomes: List[str] = Field(description="The intended learning outcomes of the course")

class CourseContentItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course content")
    unit_time_value: int = Field(description="The unit of time value for the course content")
    topic: str = Field(description="The topic per unit of time for the course content")

class PoliciesProcedures(BaseModel):
    attendance_policy: str = Field(description="The attendance policy of the class")
    late_submission_policy: str = Field(description="The late submission policy of the class")
    academic_honesty: str = Field(description="The academic honesty policy of the class")

class AssessmentMethod(BaseModel):
    type_assessment: str = Field(description="The type of assessment")
    weight: int = Field(description="The weight of the assessment in the final grade")

class AssessmentGradingCriteria(BaseModel):
    assessment_methods: List[AssessmentMethod] = Field(description="The assessment methods")
    grading_scale: dict = Field(description="The grading scale")

class LearningResource(BaseModel):
    title: str = Field(description="The book title of the learning resource")
    author: str = Field(description="The book author of the learning resource")
    year: int = Field(description="The year of creation of the book")

class CourseScheduleItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course schedule item")
    unit_time_value: int = Field(description="The unit of time value for the course schedule item")
    date: str = Field(description="The date for the course schedule item")
    topic: str = Field(description="The topic for the learning resource")
    activity_desc: str = Field(description="The descrition of the activity for the learning resource")

class SyllabusSchema(BaseModel):
    course_information: CourseInformation = Field(description="The course information")
    course_description_objectives: CourseDescriptionObjectives = Field(description="The objectives of the course")
    course_content: List[CourseContentItem] = Field(description="The content of the course")
    policies_procedures: PoliciesProcedures = Field(description="The policies procedures of the course")
    assessment_grading_criteria: AssessmentGradingCriteria = Field(description="The asssessment grading criteria of the course")
    learning_resources: List[LearningResource] = Field(description="The learning resources of the course")
    course_schedule: List[CourseScheduleItem] = Field(description="The course schedule")