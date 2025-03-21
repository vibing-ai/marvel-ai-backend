from pydantic import BaseModel, Field
from typing import List, Dict, Union
from app.services.logger import setup_logger
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from app.services.schemas import SyllabusGeneratorArgsModel
from fastapi import HTTPException

logger = setup_logger(__name__)

def get_grading_policy(grading_policy: str, grade_level: str, subject: str) -> str:
    """Returns provided grading policy or a prompt for generating one."""
    return grading_policy or f"Generate an appropriate grading policy based on the course content, {subject} subject matter, and {grade_level} level requirements"

def get_policies_expectations(policies_expectations: str, grade_level: str, subject: str) -> str:
    """Returns provided policies or a prompt for generating standard ones."""
    return policies_expectations or f"Generate standard policies and expectations appropriate for a {grade_level} level {subject} course"

def get_objectives(objectives: str, course_content: str) -> str:
    """Returns provided objectives or a prompt for generating from course content."""
    return objectives or "Generate comprehensive learning objectives based on the course content structure, ensuring each objective maps to specific topics and skills covered in the curriculum"

def get_required_materials(materials: str, grade_level: str, subject: str) -> str:
    """Returns provided materials or a prompt for generating standard requirements."""
    return materials or f"Based on the course content, recommend essential learning materials and resources appropriate for {grade_level} level {subject} instruction"

class SyllabusRequestArgs:
    def __init__(self, syllabus_generator_args: SyllabusGeneratorArgsModel, summary: str):
        # Required fields
        self._grade_level = syllabus_generator_args.grade_level
        self._subject = syllabus_generator_args.subject
        self._course_description = syllabus_generator_args.course_description
        self._course_outline = syllabus_generator_args.course_outline
        self._lang = syllabus_generator_args.lang
        
        # Optional fields with defaults
        self._summary = summary or "No summary provided"
        self._objectives = get_objectives(syllabus_generator_args.objectives, self._course_outline)
        self._required_materials = get_required_materials(syllabus_generator_args.required_materials, self._grade_level, self._subject)
        self._grading_policy = get_grading_policy(syllabus_generator_args.grading_policy, self._grade_level, self._subject)
        self._policies_expectations = get_policies_expectations(syllabus_generator_args.policies_expectations, self._grade_level, self._subject)
        self._additional_notes = syllabus_generator_args.additional_notes # can be empty

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
                # Phase 1: Course Content Generation
                "course_content": PromptTemplate(
                    template=(
                        "Generate a detailed course content structure in {lang} based on:\n\n"
                        "Course Description: {course_description}\n"
                        "Course Outline: {course_outline}\n"
                        "Course Objectives: {objectives}\n"
                        "Grade Level: {grade_level}\n"
                        "Subject: {subject}\n"
                        "Summary: {summary}\n"
                        "Additional Notes: {additional_notes}\n\n"
                        "Create a comprehensive weekly breakdown of topics, where each week contains multiple subtopics. "
                        "Format each week as a single unit with multiple related topics under it. "
                        "DO NOT create separate entries for each subtopic. Instead, combine related topics "
                        "within the same week into a single comprehensive entry.\n\n"
                        "Example format:\n"
                        "Week 1: Introduction to Linear Regression\n"
                        "- Topics covered: Basic concepts, Use cases, Variables, Scatter plots\n\n"
                        "{format_instructions}"
                    ),
                    input_variables=["course_description", "course_outline", "lang", "summary", "objectives", "grade_level", "subject", "additional_notes"],
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
                # Phase 2: Parallel Components with Strict Adherence to Course Content
                "course_information": PromptTemplate(
                    template=(
                        "Create a high-level introduction to this course in {lang}, building strictly from this course content:\n{course_content}\n\n"
                        "Grade Level: {grade_level}\n"
                        "Subject: {subject}\n\n"
                        "Guidelines:\n"
                        "1. Write an engaging course title that captures the essence of the subject\n"
                        "2. Keep the grade level as specified\n"
                        "3. Write a concise, compelling description that:\n"
                           "- Explains why this course is valuable\n"
                           "- Highlights what makes it unique\n"
                           "- Describes who would benefit from taking it\n"
                           "- Avoids listing specific topics (that's covered elsewhere)\n"
                           "- ONLY includes information present in the course content\n\n"
                        "{format_instructions}"
                    ),
                    input_variables=["grade_level", "subject", "course_content", "lang"],
                    partial_variables={"format_instructions": self.parsers["course_information"].get_format_instructions()},
                ),

                "course_description_objectives": PromptTemplate(
                    template=(
                        "Based on this course's content structure, describe the transformative outcomes and skills students will gain in {lang}. Build your response strictly from this content:\n{course_content}\n\n"
                        "Original Objectives: {objectives}\n\n"
                        "Guidelines:\n"
                        "1. Focus on OUTCOMES rather than topics:\n"
                           "- What will students be able to DO after the course?\n"
                           "- What real-world problems can they solve?\n"
                           "- What skills will they master?\n"
                           "- ONLY include outcomes related to topics covered in the course content\n\n"
                        "2. Structure the learning outcomes as:\n"
                           "- Technical Skills (e.g., 'Ability to build and validate regression models')\n"
                           "- Analytical Skills (e.g., 'Critically evaluate model assumptions')\n"
                           "- Practical Skills (e.g., 'Apply techniques to real-world datasets')\n\n"
                        "3. Make objectives SMART:\n"
                           "- Specific: Clear and unambiguous\n"
                           "- Measurable: Can be assessed\n"
                           "- Achievable: Realistic within course scope\n"
                           "- Relevant: Connected to real-world application\n"
                           "- Time-bound: Accomplishable within course duration\n\n"
                        "{format_instructions}"
                    ),
                    input_variables=["objectives", "course_content", "lang"],
                    partial_variables={"format_instructions": self.parsers["course_description_objectives"].get_format_instructions()},
                ),

                "learning_resources": PromptTemplate(
                    template=(
                        "Using ONLY this course content structure:\n{course_content}\n\n"
                        "Generate a list of learning resources in {lang}. Each resource MUST directly support "
                        "the topics defined in the course content above. DO NOT suggest resources for topics "
                        "not covered in the content structure.\n\n"
                        "Required Materials: {required_materials}\n{format_instructions}"
                    ),
                    input_variables=["course_content", "required_materials", "lang"],
                    partial_variables={"format_instructions": self.parsers["learning_resources"].get_format_instructions()},
                ),
                
                "assessment_grading_criteria": PromptTemplate(
                    template=(
                        "Using ONLY this course content structure:\n{course_content}\n\n"
                        "Define assessment methods and grading criteria in {lang}. All assessments MUST be "
                        "directly aligned with the topics and progression outlined in the course content above. "
                        "DO NOT create assessments for topics not covered in the content.\n\n"
                        "Grading Policy: {grading_policy}\n{format_instructions}"
                    ),
                    input_variables=["course_content", "grading_policy", "lang"],
                    partial_variables={"format_instructions": self.parsers["assessment_grading_criteria"].get_format_instructions()},
                ),
                # Phase 3: Course Schedule
                "course_schedule": PromptTemplate(
                    template=(
                        "Using the following inputs:\n"
                        "Course Content: {course_content}\n"
                        "Course Objectives: {course_description_objectives}\n"
                        "Assessment Methods: {assessment_grading_criteria}\n\n"
                        "DO NOT use or create information that is not present in the course content, objectives, or assessment methods.\n\n"
                        "Generate a detailed course schedule in {lang} that consolidates activities by week. "
                        "Each week should be a single entry containing:\n"
                        "1. All topics covered that week\n"
                        "2. Key activities and assignments\n"
                        "3. Learning objectives for the week\n"
                        "4. Any assessments or deadlines\n\n"
                        "Example format:\n"
                        "Week 1: Introduction to Linear Regression\n"
                        "Topics: Basic concepts, Use cases, Variables, Scatter plots\n"
                        "Activities: Introductory lecture, hands-on exercises, Homework 1\n"
                        "Objectives: Understanding fundamentals, identifying variables\n"
                        "Assessments: Homework 1 assigned\n\n"
                        "{format_instructions}"
                    ),
                    input_variables=["course_content", "course_description_objectives", "assessment_grading_criteria", "lang"],
                    partial_variables={"format_instructions": self.parsers["course_schedule"].get_format_instructions()},
                ),
            }

            # Chain1: Initial Content Generation
            chain1 = RunnableParallel(branches={
                "course_content": prompts["course_content"] | self.model | self.parsers["course_content"],
                "policies_procedures": prompts["policies_procedures"] | self.model | self.parsers["policies_procedures"]
            })

            # Chain2: Content-Dependent Components
            chain2 = RunnableParallel(branches={
                "course_information": prompts["course_information"] | self.model | self.parsers["course_information"],
                "course_description_objectives": prompts["course_description_objectives"] | self.model | self.parsers["course_description_objectives"],
                "learning_resources": prompts["learning_resources"] | self.model | self.parsers["learning_resources"],
                "assessment_grading_criteria": prompts["assessment_grading_criteria"] | self.model | self.parsers["assessment_grading_criteria"]
            })

            # Chain3: Schedule Generation
            chain3 = RunnableParallel(branches={
                "course_schedule": prompts["course_schedule"] | self.model | self.parsers["course_schedule"]
            })

            if self.verbose:
                logger.info("Successfully compiled the parallel pipeline.")

            return chain1, chain2, chain3

        except Exception as e:
            logger.error(f"Failed to compile LLM pipeline: {e}")
            raise HTTPException(status_code=500, detail="Failed to compile LLM pipeline.")


def generate_syllabus(request_args: SyllabusRequestArgs, verbose=True):
    try:
        # Initialize pipeline
        pipeline = SyllabusGeneratorPipeline(verbose=verbose)
        chain1, chain2, chain3 = pipeline.compile()
        
        # Execute Chain1: Generate initial content
        chain1_outputs = chain1.invoke(request_args.to_dict())
        course_content = chain1_outputs["branches"]["course_content"]
        policies_procedures = chain1_outputs["branches"]["policies_procedures"]
        
        # Execute Chain2: Generate content-dependent components
        chain2_inputs = {
            **request_args.to_dict(),  # Original inputs
            "course_content": course_content  # Add course_content from chain1
        }
        chain2_outputs = chain2.invoke(chain2_inputs)
        
        # Execute Chain3: Generate course schedule
        chain3_inputs = {
            **request_args.to_dict(),
            "course_content": course_content,
            "course_description_objectives": chain2_outputs["branches"]["course_description_objectives"],
            "assessment_grading_criteria": chain2_outputs["branches"]["assessment_grading_criteria"],
        }
        chain3_outputs = chain3.invoke(chain3_inputs)

        if verbose:
            logger.debug(f"Chain1 Outputs: {chain1_outputs}")
            logger.debug(f"Chain2 Outputs: {chain2_outputs}")
            logger.debug(f"Chain3 Outputs: {chain3_outputs}")
        
        # Combine all outputs into final schema
        model = SyllabusSchema(
            course_information=chain2_outputs["branches"]["course_information"],
            course_description_objectives=chain2_outputs["branches"]["course_description_objectives"],
            course_content=course_content,  
            policies_procedures=policies_procedures,  
            assessment_grading_criteria=chain2_outputs["branches"]["assessment_grading_criteria"],
            learning_resources=chain2_outputs["branches"]["learning_resources"],
            course_schedule=chain3_outputs["branches"]["course_schedule"]
        )
        
        return dict(model)

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate syllabus from LLM.")

    
class CourseInformation(BaseModel):
    course_title: str = Field(description="The course title")
    grade_level: str = Field(description="The grade level")
    description: str = Field(description="The course description")

class LearningOutcome(BaseModel):
    category: str
    outcomes: List[str]

class CourseDescriptionObjectives(BaseModel):
    objectives: List[str]
    intended_learning_outcomes: Union[List[str], List[LearningOutcome]]

class CourseContentItem(BaseModel):
    unit_time: str = Field(description="The unit of time (e.g., week)")
    unit_time_value: int = Field(description="The week number")
    main_topic: str = Field(description="The main topic for this week")
    subtopics: List[str] = Field(description="List of subtopics covered this week")

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
    unit_time: str = Field(description="The unit of time (e.g., week)")
    unit_time_value: int = Field(description="The week number")
    main_topic: str = Field(description="The main topic for this week")
    topics: List[str] = Field(description="List of topics covered")
    activities: List[str] = Field(description="List of activities and assignments")
    objectives: List[str] = Field(description="Learning objectives for the week")
    assessments: List[str] = Field(description="Assessments and deadlines")

class SyllabusSchema(BaseModel):
    course_information: CourseInformation = Field(description="The course information")
    course_description_objectives: CourseDescriptionObjectives = Field(description="The objectives of the course")
    course_content: List[CourseContentItem] = Field(description="The content of the course")
    policies_procedures: PoliciesProcedures = Field(description="The policies procedures of the course")
    assessment_grading_criteria: AssessmentGradingCriteria = Field(description="The asssessment grading criteria of the course")
    learning_resources: List[LearningResource] = Field(description="The learning resources of the course")
    course_schedule: List[CourseScheduleItem] = Field(description="The course schedule")