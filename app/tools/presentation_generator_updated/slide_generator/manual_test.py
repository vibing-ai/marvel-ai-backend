from image_utils import build_prompt, call_image_api, get_image_size

title = "Photosynthesis Process"
content = ["Sunlight absorption", "Chlorophyll activation", "Oxygen release"]
layout = "titleBullets"

prompt = build_prompt(title, content, layout)
width, height = get_image_size(layout)

image_url = call_image_api(prompt, width, height)
print("✅ Generated Image URL:", image_url)
