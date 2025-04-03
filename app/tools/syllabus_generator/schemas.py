from pydantic import BaseModel, Field, validator
from typing import List, Union

class CourseInformation(BaseModel):
    course_title: str = Field(description="The course title")
    grade_level: str = Field(description="The grade level")
    description: str = Field(description="The course description")
    @validator('course_title', pre=True)
    def validate_course_title(cls, v):
        if not v or v == "Not specified":
            return "General Course"
        return v
        
    @validator('grade_level', pre=True)
    def validate_grade_level(cls, v):
        if not v or v == "Not specified":
            return "Unspecified Grade Level"
        return v
        
    @validator('description', pre=True)
    def validate_description(cls, v):
        if not v or v == "":
            return "This course provides students with knowledge and skills in the subject area."
        return v

class CourseDescriptionObjectives(BaseModel):
    objectives: List[str] = Field(description="The course objectives")
    intended_learning_outcomes: List[str] = Field(description="The intended learning outcomes of the course")

class CourseContentItem(BaseModel):
    unit_sequence: int = Field(description="The sequential unit/module number")
    title: str = Field(description="The title of the unit")
    description: str = Field(description="A brief summary of the unit's content")
    key_topics: List[str] = Field(description="The key topics for the unit")
    learning_outcomes: List[str] = Field(description="The learning outcomes for the unit")

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
    session_number: int = Field(description="The sequential session number in the course")
    date: str = Field(description="The scheduled date for this session (format: YYYY-MM-DD)")
    time_frame: str = Field(description="The duration of the session (e.g., '2 days', '1 week', '1 month')")
    topic: str = Field(description="The topic for the learning resource")
    activity_desc: str = Field(description="A brief description of the planned learning activity for this session")

class FallbackResponse(BaseModel):
    status: str = Field(description="The status of the response")
    error: str = Field(description="The error message")
    section: str = Field(description="The section of the response")
    fallback: bool = Field(description="The fallback status")
    
class SyllabusSchema(BaseModel):
    course_information: Union[CourseInformation, FallbackResponse] = Field(description="The course information")
    course_description_objectives: Union[CourseDescriptionObjectives, FallbackResponse] = Field(description="The objectives of the course")
    course_content: Union[List[CourseContentItem], FallbackResponse] = Field(description="The content of the course")
    policies_procedures: Union[PoliciesProcedures, FallbackResponse] = Field(description="The policies procedures of the course")
    assessment_grading_criteria: Union[AssessmentGradingCriteria, FallbackResponse] = Field(description="The asssessment grading criteria of the course")
    learning_resources: Union[List[LearningResource], FallbackResponse] = Field(description="The learning resources of the course")
    course_schedule: Union[List[CourseScheduleItem], FallbackResponse] = Field(description="The course schedule")
    