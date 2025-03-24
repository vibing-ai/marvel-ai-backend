def build_prompt(title: str, content: list, layout: str = "") -> str:
    bullet_points = ', '.join(content)
    prompt = (
        f"An educational slide illustration titled '{title}', "
        f"covering: {bullet_points}. "
        f"Style: minimalist, clean. Suitable for layout '{layout}'."
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
    # ⚠️ Replace this with Imagen 3 or Flux 1.1 API call later
    print(f"Calling image model with: {prompt} ({width}x{height})")
    return "https://fake.image.generated/from-prompt.jpg"
