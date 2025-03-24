from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.tools.presentation_generator_updated.slide_generator.image_utils import build_prompt, get_image_size, call_image_api

router = APIRouter()

class SlideImageRequest(BaseModel):
    title: str
    content: List[str]
    layout: Optional[str] = "titleBullets"

@router.post("/generate-slide-image")
def generate_slide_image(request: SlideImageRequest):
    try:
        prompt = build_prompt(request.title, request.content, request.layout)
        width, height = get_image_size(request.layout)
        image_url = call_image_api(prompt, width, height)
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
