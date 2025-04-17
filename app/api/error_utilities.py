from pydantic import BaseModel
from typing import Any

class VideoTranscriptError(Exception):
    """Raised when a video transcript cannot be loaded. Used for tools which require video transcripts."""
    def __init__(self, message, url):
        self.message = message
        self.url = url
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"

class InputValidationError(Exception):
    """Raised when an input validation error occurs."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class LoaderError(Exception):
    """Raised when a tool module's loader function encounters an error."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ToolExecutorError(Exception):
    """Raised when a tool executor encounters an error."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ErrorResponse(BaseModel):
    """Base model for error responses."""
    status: int
    message: Any
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class FileHandlerError(Exception):
    """Raised when a file content cannot be loaded. Used for tools which require file handling."""
    def __init__(self, message, url=None):
        self.message = message
        self.url = url
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"

class ImageHandlerError(Exception):
    """Raised when an image cannot be loaded. Used for tools which require image handling."""
    def __init__(self, message, url):
        self.message = message
        self.url = url
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"
    
class WorksheetGeneratorError(Exception):
    """Base class for errors related to the worksheet generator."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    
class SyllabusGeneratorError(Exception):
    """Base class for errors related to the syllabus generator."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

#Image generation errors
class ImageGenerationError(Exception):
    """Raised when an image generation error occurs."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)



