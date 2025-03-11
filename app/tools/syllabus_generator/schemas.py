from pydantic import BaseModel, Field
from typing import List, Union

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

class CourseContentItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course content")
    unit_time_value: int = Field(description="The unit of time value for the course content")
    topic: str = Field(description="The topic per unit of time for the course content")

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
