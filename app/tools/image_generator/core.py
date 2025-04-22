import logging
from app.schemas import ImagePrompt, ImageResponse
from app.tools.image_generator.tools import generate_image_with_vertex_ai, enhance_prompt, is_prompt_safe

logger = logging.getLogger(__name__)

def generate_educational_image(prompt_data: ImagePrompt) -> ImageResponse:
    """
    Execute the image generation pipeline using Vertex AI.
    Prompt enhancement and safety checks are handled by tools.py.
    """
    try:
        # Enhance the prompt
        enhanced_prompt = enhance_prompt(
            prompt_data.prompt,
            subject=prompt_data.subject,
            grade_level=prompt_data.grade_level
        )

        # Check prompt safety
        if not is_prompt_safe(enhanced_prompt):
            logger.warning(f"Blocked unsafe prompt: '{enhanced_prompt}'")
            return ImageResponse(
                image_url="",
                prompt_used=enhanced_prompt,
                success=False,
                error_message="Prompt rejected due to unsafe content"
            )

        # Generate image using Vertex AI (delegated to tools.py)
        image_data = generate_image_with_vertex_ai(enhanced_prompt)

        logger.info(f"Successfully generated image for prompt: '{enhanced_prompt}'")
        return ImageResponse(
            image_url=image_data,
            prompt_used=enhanced_prompt,
            success=True,
            error_message=""
        )

    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return ImageResponse(
            image_url="",
            prompt_used=prompt_data.prompt,
            success=False,
            error_message=f"Image generation failed: {str(e)}"
        )