import sys
import os
# Dynamically add the project root to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import uvicorn
from fastapi import FastAPI, HTTPException
from app.features.text_rewriter.router import router 
from app.features.text_rewriter.core import logger 
from app.features.text_rewriter.tools import (
    load_metadata,
    create_input_schema,
    create_output_schema,
    rewrite_tool_handler,
    get_few_shot_examples
)

# Load metadata.json
metadata = load_metadata()

# Dynamically create Pydantic models
InputModel = create_input_schema(metadata)
OutputModel = create_output_schema(metadata)

# Initialize FastAPI app
app = FastAPI(
    title="Text Rewriter API",
    description="FastAPI application for text rewriting.",
    version="2.0.0"
)

# Include your router with the rewrite_text endpoint
app.include_router(router)

@app.post("/rewrite-text", response_model=OutputModel)
async def rewrite_text(data: InputModel):
    """
    FastAPI endpoint for rewriting text based on metadata.json.
    """
    try:
        # Convert Pydantic model to dict and validate inputs
        inputs = data.dict()

        # Get the few-shot examples to pass along
        few_shot_examples = get_few_shot_examples()

        # Log input and few-shot examples for debugging
        logger.info(f"Few-shot examples: {few_shot_examples}")

        # Call the rewrite tool handler with both inputs and few-shot examples
        result = rewrite_tool_handler(inputs, few_shot_examples)

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Run the app
if __name__ == "__main__":
    uvicorn.run("app.features.text_rewriter.test_core:app", host="0.0.0.0", port=8000, reload=True)