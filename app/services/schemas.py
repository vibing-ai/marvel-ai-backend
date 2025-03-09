from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal, Union
from enum import Enum
from app.services.assistant_registry import AssistantInputs
from app.services.tool_registry import BaseTool

class User(BaseModel):
    id: str
    fullName: str
    email: str
    
class Role(str, Enum):
    human = "human"
    ai = "ai"
    system = "system"

class MessageType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    file = "file"

class MessagePayload(BaseModel):
    text: Union[str, dict]

class Message(BaseModel):
    role: Role
    type: MessageType
    timestamp: Optional[Any] = None
    payload: MessagePayload
    
class RequestType(str, Enum):
    chat = "chat"
    tool = "tool"

class GenericRequest(BaseModel):
    user: User
    type: RequestType
    
class ChatRequest(GenericRequest):
    messages: List[Message]

class GenericAssistantRequest(BaseModel):
    assistant_inputs: AssistantInputs
    
class ToolRequest(GenericRequest):
    tool_data: BaseTool
    
class ChatResponse(BaseModel):
    data: List[Message]

class ToolResponse(BaseModel):
    data: Any
    
class ChatMessage(BaseModel):
    role: str
    type: str
    text: str

class QuizzifyArgs(BaseModel):
    topic: str
    n_questions: int
    file_url: str
    file_type: str
    lang: Optional[str] = "en"

class WorksheetQuestion(BaseModel):
    question_type: str
    number: int
    
class WorksheetQuestionModel(BaseModel):
    worksheet_question_list: List[WorksheetQuestion]

class WorksheetGeneratorArgs(BaseModel):
    grade_level: str
    topic: str
    worksheet_list: WorksheetQuestionModel
    file_url: str
    file_type: str
    lang: Optional[str] = "en"
    
class SyllabusGeneratorArgsModel(BaseModel):
    grade_level: str
    subject: str
    course_description: str
    objectives: str
    required_materials: str
    grading_policy: str
    policies_expectations: str
    course_outline: str
    additional_notes: str
    file_url: str
    file_type: str
    lang: Optional[str] = "en"
    
class AIResistantArgs(BaseModel):
    assignment: str = Field(..., max_length=255, description="The given assignment")
    grade_level: Literal["pre-k", "kindergarten", "elementary", "middle", "high", "university", "professional"] = Field(..., description="Educational level to which the content is directed")
    file_type: str = Field(..., description="Type of file being handled, according to the defined enumeration")
    file_url: str = Field(..., description="URL or path of the file to be processed")
    lang: str = Field(..., description="Language in which the file or content is written")
    
class ConnectWithThemArgs(BaseModel):
    grade_level: str = Field(..., description="The grade level the teacher is instructing.")
    task_description: str = Field(..., description="A brief description of the subject or topic the teacher is instructing.")
    students_description: str = Field(..., description="A description of the students including age group, interests, location, and any relevant cultural or social factors.")
    task_description_file_url: str 
    task_description_file_type: str 
    student_description_file_url: str
    student_description_file_type: str
    lang: str = Field(..., description="The language in which the subject is being taught.")

# Changed request schema to match the new functionality of the presentation generator
class PresentationGeneratorArgs(BaseModel):
    grade_level: str
    n_slides: int
    topic: str
    objectives: str
    lang: Optional[str] = "en"

class RubricGeneratorArgs(BaseModel):
    grade_level: Literal["pre-k", "kindergarten", "elementary", "middle", "high", "university", "professional"]
    point_scale: int
    objectives: str
    assignment_description: str
    objectives_file_url: str
    objectives_file_type: str
    assignment_description_file_url: str
    assignment_description_file_type: str
    lang: Optional[str]

class LessonPlanGeneratorArgs(BaseModel):
    grade_level: str
    topic: str
    objectives: str
    additional_customization: str
    objectives_file_url: str
    objectives_file_type: str
    additional_customization_file_url: str
    additional_customization_file_type: str
    lang: Optional[str] = "en"

class WritingFeedbackGeneratorArgs(BaseModel):
    grade_level: str
    assignment_description: str
    criteria: str
    writing_to_review: str
    criteria_file_url: str
    criteria_file_type: str
    writing_to_review_file_url: str
    writing_to_review_file_type: str
    lang: Optional[str] = "en"