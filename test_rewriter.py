
from app.tools.text_rewriter.core import executor

# Test different styles
text = "The cat sat on the mat. It was looking at a bird flying nearby."
styles = ["formal", "casual", "academic", "professional"]

for style in styles:
    print(f"\nTesting {style.upper()} style:")
    result = executor(text=text, rewrite_style=style, lang="en", verbose=True)
    print(f"Original: {result.original}")
    print(f"Rewritten: {result.rewritten}")
    print(f"Changes: {result.changes_explained}")
    print("-" * 50)
