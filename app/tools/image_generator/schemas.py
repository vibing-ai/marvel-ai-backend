from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal, Union



class ImageGeneratorArgs(BaseModel):
    prompt: str
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    presets: Optional[dict] = None
    lang: Optional[str] = "en"   
    style: Optional[str] = None