# Pull Request Summary: Slide Image Generation Integration

## ✅ Completed Work
- Integrated image generation logic into the slide generator pipeline.
- Implemented `build_prompt()` to structure educational image prompts based on slide content and layout.
- Added `needs_image()` heuristic to prevent unnecessary image generation.
- Created `call_image_api()` stub for Imagen 3 (currently uses Gemini placeholder).
- Created test suite:
  - Prompt structure validation
  - Edge cases for content types
  - Image size and heuristic logic
- All unit tests are passing ✅

## 📂 New Files Added
- `image_utils.py`: Contains `build_prompt`, `needs_image`, `call_image_api`, and layout-specific logic.
- `manual_test.py`: Simple test script for running prompt/image generation manually.
- `test_prompt_generator.py`: Unit tests for prompt generation logic.
- `test_image_utils.py`: Future space for API call tests.

## 🤔 Reviewer Notes
- Please suggest any refinements to:
  - Prompt clarity
  - Style-to-layout mapping
  - `needs_image()` logic
- Let me know if you’d prefer the image generation moved to a background task queue for scalability.

## 🛠️ Next Steps (Planned)
- Replace fake `call_image_api()` with real **Flux 1.1** integration via Replicate or local install.
- Evaluate image quality, latency, and cost of Imagen 3 vs. Flux 1.1.
- Store generated image URLs in cloud storage (e.g., GCS or Firebase).
- Consider implementing batching for prompt generation.

Thanks for reviewing!
