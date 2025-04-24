from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing    import Optional

NonEmptyStr = str  # we’ll enforce the length in the validator

class ImageGenerationInput(BaseModel):
    base_prompt: NonEmptyStr = Field(..., description="Base text prompt")
    grade_level: NonEmptyStr = Field(..., description="Target grade level")
    subject:     NonEmptyStr = Field(..., description="Subject for the image")
    language:    Optional[str] = Field(
        None,
        description="Prompt language (optional).",
    )

    # ---------- single validator for all three required fields ----------
    @field_validator("base_prompt", "grade_level", "subject")
    @classmethod
    def must_not_be_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            # customise the message however you like
            raise ValueError(f"'{info.field_name}' Cannot be empty.")
        return v

class ImageGenerationOutput(BaseModel):
    image_url: NonEmptyStr = Field(..., description="URL of the generated image")
