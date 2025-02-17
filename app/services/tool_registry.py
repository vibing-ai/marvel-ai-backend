from pydantic import BaseModel
from app.services.logger import setup_logger
from typing import List, Any, Optional, Dict
from app.api.error_utilities import InputValidationError

logger = setup_logger(__name__)

class ToolInput(BaseModel):
    # Input from incoming request typically represent HTML Form elements
    name: str
    value: Any
    # When passing "files", the value field is an object with file details as properties
    
# Base model for all tools
class BaseTool(BaseModel):
<<<<<<< HEAD
    tool_id: str  # Unique identifier for each tool,
=======
    tool_id: int  # Unique identifier for each tool,

    inputs: List[ToolInput]

class ToolFile(BaseModel):
    filePath: Optional[str] = None
    url: str
    filename: Optional[str] = None