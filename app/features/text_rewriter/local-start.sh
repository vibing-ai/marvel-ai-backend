#!/bin/bash
source env/bin/activate  # Activate virtual environment
uvicorn text_rewriter:app --reload  # Start the FastAPI server
