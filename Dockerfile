# backend/Dockerfile
FROM python:3.10.12

WORKDIR /code

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy credentials file
COPY marvel-ai-backend-credentials.json /code/marvel-ai-backend-credentials.json

COPY ./app /code/app

# Local development key set
# ENV TYPES: dev, production
# When set to dev, API Key on endpoint requests are just 'dev'
# When set to production, API Key on endpoint requests are the actual API Key

ENV PYTHONPATH=/code/app

CMD ["fastapi", "dev", "app/main.py", "--host=0.0.0.0", "--port=8000"]