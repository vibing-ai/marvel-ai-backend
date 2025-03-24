# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables for non-interactive installs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory inside the container
WORKDIR /code/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

# Copy the application source code into the container
COPY . /code/app

# Copy the .env file into the container
COPY app/features/text_rewriter/text_rewriter.env /code/app/features/text_rewriter/

# Set the virtual environment as the default Python environment
ENV PATH="/venv/bin:$PATH"

# Expose the application port
EXPOSE 8000

# Use uvicorn to run the FastAPI app from test_core.py (where the /rewrite-text route is defined)
ENTRYPOINT ["uvicorn", "app.features.text_rewriter.test_core:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]