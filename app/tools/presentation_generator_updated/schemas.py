from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal, Union


class OutlineGeneratorInput(BaseModel):
    n_slides: int
    topic: str
    instructional_level: str
    file_url: str
    file_type: str
    lang: Optional[str] = "en"

class SlideGeneratorInput(BaseModel):
    slides_titles: List[str]
    instructional_level: str
    topic: str
    file_url: str
    file_type: str
    lang: Optional[str] = "en"