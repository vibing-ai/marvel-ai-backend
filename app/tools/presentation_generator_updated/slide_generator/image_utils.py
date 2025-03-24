from typing import Union
import os
import google.generativeai as genai


def build_prompt(
    title: str,
    content: Union[str, list, dict],
    layout: str = "",
    style: str = "clean, modern",
    tone: str = "educational"
) -> str:
    # ✂️ Normalize and truncate content for prompt readability
    def format_content(c):
        if isinstance(c, list):
            return ', '.join(map(str, c[:5]))  # Limit to first 5 items
        elif isinstance(c, dict):
            return ', '.join(f"{k}: {v}" for k, v in list(c.items())[:5])
        else:
            return str(c)

    # 🔒 Sanitize title and content for prompt safety
    title = title.replace("{", "").replace("}", "").replace('"', "'")
    content_text = format_content(content).replace("{", "").replace("}", "").replace('"', "'")

    # 🎨 Style recommendations per layout
    layout_styles = {
        "titleBody": "a centered diagram with labels and arrows",
        "titleBullets": "an infographic using simple icons and short keywords",
        "twoColumn": "a split-view image comparing two key ideas side by side",
        "sectionHeader": "a bold, hero-style image with minimal text"
    }
    visual_style = layout_styles.get(layout, "a minimalist educational illustration for a default layout")

    # 🖼️ Compose the final prompt
    prompt = (
        f"Create an educational slide illustration titled '{title}'. "
        f"It should visually represent the following concepts: {content_text}. "
        f"Depict the slide using {visual_style}. "
        f"The image must be {style} and suitable for a {tone} setting."
    )

    return prompt


def get_image_size(layout: str):
    sizes = {
        "titleBody": (1280, 720),
        "titleBullets": (1024, 768),
        "twoColumn": (800, 600),
        "sectionHeader": (1600, 900)
    }
    return sizes.get(layout, (1024, 768))  # Default fallback


def call_image_api(prompt: str, width: int, height: int) -> str:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

    model = genai.GenerativeModel(model_name="models/imagegenerator")

    response = model.generate_content(
        {
            "prompt": prompt,
            "image_config": {
                "width": width,
                "height": height,
                "style": "realistic",
                "quality": "high"
            }
        }
    )

    # Check if URL is returned
    if hasattr(response, 'candidates') and response.candidates:
        image_url = response.candidates[0].image.url
        return image_url

    raise ValueError("No image URL returned from Imagen 3.")


def needs_image(title: str, content: Union[str, list, dict], layout: str) -> bool:
    # 🚦 Basic rules for whether to generate an image
    title_lower = title.strip().lower()
    if "title" in title_lower or "introduction" in title_lower:
        return False

    if isinstance(content, list) and len(content) >= 3:
        return True
    if isinstance(content, dict) and len(content) >= 2:
        return True
    if isinstance(content, str) and len(content) > 100:
        return True

    if layout in ["twoColumn", "titleBullets"]:
        return True

    return False