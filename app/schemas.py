from pydantic import BaseModel, Field
from typing import Optional

class ImagePrompt(BaseModel):
    prompt: str = Field(..., min_length=1, description="Text prompt for image generation")
    subject: Optional[str] = Field(None, description="Subject area (e.g., biology)")
    grade_level: Optional[str] = Field(None, description="Grade level (e.g., middle school)")

class ImageResponse(BaseModel):
    image_url: str = Field(..., description="URL or base64 string of the generated image")
    prompt_used: str = Field(..., description="The prompt processed to generate the image")
    success: bool = Field(True, description="Whether generation succeeded")
    error_message: Optional[str] = Field(None, description="Error details if generation failed")