from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from app.services.logger import setup_logger

from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.features.syllabus_generator.document_loaders import read_text_file
from app.services.schemas import SyllabusGeneratorArgsModel

from fastapi import HTTPException


logger = setup_logger(__name__)

class SyllabusRequestArgs:
    def __init__(self, 
                 syllabus_generator_args: SyllabusGeneratorArgsModel,
                 summary: str):
        
        self._grade_level = syllabus_generator_args.grade_level
        self._course = syllabus_generator_args.course
        self._instructor_name = syllabus_generator_args.instructor_name
        self._instructor_title = syllabus_generator_args.instructor_title
        self._unit_time = syllabus_generator_args.unit_time
        self._unit_time_value = syllabus_generator_args.unit_time_value
        self._start_date = syllabus_generator_args.start_date
        self._assessment_methods = syllabus_generator_args.assessment_methods
        self._grading_scale = syllabus_generator_args.grading_scale
        self._lang = syllabus_generator_args.lang
        self._summary = summary

    @property
    def grade_level(self) -> str:
        return self._grade_level

    @property
    def course(self) -> str:
        return self._course

    @property
    def instructor_name(self) -> str:
        return self._instructor_name

    @property
    def instructor_title(self) -> str:
        return self._instructor_title

    @property
    def unit_time(self) -> str:
        return self._unit_time
    
    @property
    def unit_time_value(self) -> int:
        return self._unit_time_value

    @property
    def start_date(self) -> str:
        return self._start_date

    @property
    def assessment_methods(self) -> str:
        return self._assessment_methods

    @property
    def grading_scale(self) -> str:
        return self._grading_scale
    
    @property
    def lang(self) -> str:
        return self._lang
    
    @property
    def summary(self) -> str:
        return self._summary
    
    def to_dict(self) -> dict:
        return {
            "grade_level": self.grade_level,
            "course": self.course,
            "instructor_name": self.instructor_name,
            "instructor_title": self.instructor_title,
            "unit_time": self.unit_time,
            "unit_time_value": self.unit_time_value,
            "start_date": self.start_date,
            "assessment_methods": self.assessment_methods,
            "grading_scale": self.grading_scale,
            "lang": self.lang,
            "summary": self.summary
        }
    

class SyllabusGeneratorPipeline:
    def __init__(self, prompt=None, parser=None, model=None, verbose=False):
        default_config = {
            "prompt": read_text_file("prompt/syllabus_generator-prompt.txt"),
            "parser": JsonOutputParser(pydantic_object=SyllabusSchema),
            "model": GoogleGenerativeAI(model="gemini-1.5-pro")
        }
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.verbose = verbose

    def compile(self):
        try:
            prompt = PromptTemplate(
                template=self.prompt,
                input_variables=[
                    "grade_level", 
                    "course",
                    "instructor_name",
                    "instructor_title",
                    "unit_time",
                    "unit_time_value",
                    "start_date",
                    "assessment_methods",
                    "grading_scale",
                    "summary"
                    ],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )

            chain = prompt | self.model | self.parser

            if self.verbose: logger.info(f"Chain compilation complete")

        except Exception as e:
            logger.error(f"Failed to compile LLM chain : {e}")
            raise HTTPException(status_code=500, detail=f"Failed to compile LLM chain")
        
        return chain

class CourseInformation(BaseModel):
    course_title: str = Field(description="The course title")
    grade_level: str = Field(description="The grade level")
    description: str = Field(description="The course description")

class InstructorInformation(BaseModel):
    name: str = Field(description="The instructor name")
    title: str = Field(description="The instructor title")
    description_title: str = Field(description="The description of the instructor title")

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
    instructor_information: InstructorInformation = Field(description="The instructor information")
    course_description_objectives: CourseDescriptionObjectives = Field(description="The objectives of the course")
    course_content: List[CourseContentItem] = Field(description="The content of the course")
    policies_procedures: PoliciesProcedures = Field(description="The policies procedures of the course")
    assessment_grading_criteria: AssessmentGradingCriteria = Field(description="The asssessment grading criteria of the course")
    learning_resources: List[LearningResource] = Field(description="The learning resources of the course")
    course_schedule: List[CourseScheduleItem] = Field(description="The course schedule")

    model_config = {
        "json_schema_extra": {
            "examples": """
            {
                "course_information": {
                    "course_title": "Linear Algebra",
                    "grade_level": "Undergraduate",
                    "description": "This course covers the fundamental concepts of linear algebra including vector spaces, linear transformations, matrices, and eigenvalues."
                },
                "instructor_information": {
                    "name": "Wilfredo Sosa",
                    "title": "Professor of Mathematics",
                    "description_title": "Experienced educator with a focus on advanced mathematical theories and applications."
                },
                "course_description_objectives": {
                    "objectives": [
                    "Understand the basic principles of vector spaces and linear transformations.",
                    "Apply matrix operations and solve linear systems.",
                    "Analyze eigenvalues and eigenvectors and their applications."
                    ],
                    "intended_learning_outcomes": [
                    "Students will be able to explain the concept of a vector space and a linear transformation.",
                    "Students will be able to perform matrix operations and solve linear systems.",
                    "Students will be able to determine eigenvalues and eigenvectors and understand their significance."
                    ]
                },
                "course_content": [
                    {
                    "unit_time": "week",
                    "unit_time_value": 1,
                    "topic": "Introduction to Linear Algebra"
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 2,
                    "topic": "Vector Spaces"
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 3,
                    "topic": "Linear Transformations"
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 4,
                    "topic": "Matrix Operations"
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 5,
                    "topic": "Solving Linear Systems"
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 6,
                    "topic": "Eigenvalues and Eigenvectors"
                    }
                ],
                "policies_procedures": {
                    "attendance_policy": "Attendance is mandatory and will be recorded for every class.",
                    "late_submission_policy": "Late submissions will be penalized at 10% per day unless prior arrangements are made.",
                    "academic_honesty": "All students are expected to adhere to the university's academic honesty policy. Cheating and plagiarism are strictly prohibited."
                },
                "assessment_grading_criteria": {
                    "assessment_methods": [
                    {
                        "type": "Assignment",
                        "weight": 20
                    },
                    {
                        "type": "Midterm Exam",
                        "weight": 30
                    },
                    {
                        "type": "Final Exam",
                        "weight": 50
                    }
                    ],
                    "grading_scale": {
                    "A": "90-100%",
                    "B": "80-89%",
                    "C": "70-79%",
                    "D": "60-69%",
                    "F": "below 60%"
                    }
                },
                "learning_resources": [
                    {
                    "title": "Linear Algebra and Its Applications",
                    "author": "David C. Lay",
                    "year": 2015
                    },
                    {
                    "title": "Introduction to Linear Algebra",
                    "author": "Gilbert Strang",
                    "year": 2016
                    }
                ],
                "course_schedule": [
                    {
                    "unit_time": "week",
                    "unit_time_value": 1,
                    "date": "2024-09-01",
                    "topic": "Introduction to Linear Algebra",
                    "activity_desc": "Overview of course structure and key concepts."
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 2,
                    "date": "2024-09-08",
                    "topic": "Vector Spaces",
                    "activity_desc": "Understanding the properties and examples of vector spaces."
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 3,
                    "date": "2024-09-15",
                    "topic": "Linear Transformations",
                    "activity_desc": "Exploring linear mappings between vector spaces."
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 4,
                    "date": "2024-09-22",
                    "topic": "Matrix Operations",
                    "activity_desc": "Performing addition, multiplication, and inversion of matrices."
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 5,
                    "date": "2024-09-29",
                    "topic": "Solving Linear Systems",
                    "activity_desc": "Methods for solving systems of linear equations."
                    },
                    {
                    "unit_time": "week",
                    "unit_time_value": 6,
                    "date": "2024-10-06",
                    "topic": "Eigenvalues and Eigenvectors",
                    "activity_desc": "Introduction to eigenvalues and eigenvectors and their applications."
                    }
                ]
            }
        """
        }
    }


def generate_syllabus(request_args, verbose=True):
    try:
        pipeline = SyllabusGeneratorPipeline(verbose=verbose)
        chain = pipeline.compile()
        output = chain.invoke(request_args.to_dict())

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate syllabus from LLM")

    return output