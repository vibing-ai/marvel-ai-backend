![image](https://github.com/user-attachments/assets/04e5f5a4-9ba7-4887-a158-bca181f7391c)

# Marvel AI Platform

![Static Badge](https://img.shields.io/badge/v3.10.12-blue?logo=python&logoColor=yellow&labelColor=gray)
![Static Badge](https://img.shields.io/badge/Gemini%201.0-blue?logo=googlegemini&logoColor=blue&labelColor=gray)
![Static Badge](https://img.shields.io/badge/Vertex%20AI-blue?logo=googlecloud&logoColor=white&labelColor=gray)
![Static Badge](https://img.shields.io/badge/FastAPI-blue?logo=fastapi&logoColor=white&labelColor=gray)

## Table of Contents

1. [Architecture](#architecture)
2. [Folder Structure](#folder-structure)
3. [Installation](#installation)
   - [Navigate to the App Directory](#navigate-to-the-app-directory)
   - [Create and Activate Virtual Environment](#create-and-activate-virtual-environment)
   - [Install Required Libraries](#install-required-libraries)
4. [Running Locally and Testing](#running-locally-and-testing)
   - [Prerequisites](#prerequisites)
   - [Steps for Authentication Setup](#steps-for-authentication-setup)
     - [Step 1: Create a Google Cloud Project](#step-1-create-a-google-cloud-project)
     - [Step 2: Enable the Google Cloud APIs](#step-2-enable-the-google-cloud-apis)
     - [Step 3: Create a new AI Studio API Key](#step-3-create-a-new-ai-studio-api-key)
     - [Step 4: Create a new .env and Store the API Key](#step-4-create-a-new-env-and-store-the-api-key)
     - [Step 5: Run the Application with Local Shell Script](#step-5-run-the-application-with-local-shell-script)
     - [Step 6: Set the API Header](#step-6-set-the-api-header)
5. [Docker Setup Guide](#docker-setup-guide)
   - [Overview](#overview)
   - [Prerequisites for Docker](#prerequisites-for-docker)
   - [Installation Instructions](#installation-instructions)
     - [Step 1: Build the Docker Image](#step-1-build-the-docker-image)
     - [Step 2: Run the Docker Container](#step-2-run-the-docker-container)
6. [Environment Variables](#environment-variables)
7. [Accessing the Application](#accessing-the-application)

## Architecture
  ![Architecture](diagram.png)

## Folder Structure

```plaintext
marvel-ai-backend/
├── app/                     # Contains the main application code
│   ├── api/                 # Contains the API router for handling requests
<<<<<<< HEAD
│   │   └── router.py        # Endpoints for FastAPI to test features and handle incoming requests
│   │   └── error_utilities.py  
│   ├── assistants/            # Contains the MarvelAI tools
│   │   ├── assistant_group1/
│   │   │   ├── assistant1/
│   │   │   │   │   ├── prompt/
│   │   │   │   │   ├── tests/
│   │   │   │   │   ├── core.py
│   │   │   │   │   ├── tools.py
│   │   │   │   │   └── metadata.json
│   │   │   ├── assistant2/
│   │   │   │   │   ├── prompt/
│   │   │   │   │   ├── tests/
│   │   │   │   │   ├── core.py
│   │   │   │   │   ├── tools.py
│   │   │   │   │   └── metadata.json
│   │   │   ├── assistantN/
│   │   │   │   │   ├── prompt/
│   │   │   │   │   ├── tests/
│   │   │   │   │   ├── core.py
│   │   │   │   │   ├── tools.py
│   │   │   │   │   └── metadata.json
│   │   ├── assistant_group2/
│   │   ├── assistant_groupN/
│   │   ├── utils/
│   │   │   ├── assistants_utilities.py
│   │   │   └── assistants_config.json       
│   ├── tools/            # Contains the MarvelAI tools
│   │   ├── tool1/
=======
│   │   ├── tests/
│   │   └── router.py        # Endpoints for FastAPI to test features and handle incoming requests
│   │   └── error_utilities.py        
│   │   └── tool_utilities.py        
│   │   └── tools_config.json        
│   ├── features/            # Contains feature-specific modules
│   │   ├── feature1/
>>>>>>> 2cf0cdd2b47b630ac2959e0306bf0ccbed67e10b
│   │   │   ├── core.py
│   │   │   ├── tools.py
│   │   │   ├── prompt/
│   │   │   ├── tests/
│   │   │   └── metadata.json
<<<<<<< HEAD
│   │   ├── tool2/
=======
│   │   ├── feature2/
>>>>>>> 2cf0cdd2b47b630ac2959e0306bf0ccbed67e10b
│   │   │   ├── core.py
│   │   │   ├── tools.py
│   │   │   ├── prompt/
│   │   │   ├── tests/
│   │   │   └── metadata.json
<<<<<<< HEAD
│   │   ├── toolN/
=======
│   │   ├── featureN/
>>>>>>> 2cf0cdd2b47b630ac2959e0306bf0ccbed67e10b
│   │   │   ├── core.py
│   │   │   ├── tools.py
│   │   │   ├── prompt/
│   │   │   ├── tests/
│   │   │   └── metadata.json
<<<<<<< HEAD
│   │   ├── utils/
│   │   │   ├── tool_utilities.py
│   │   │   └── tools_config.json
│   ├── services/            # Contains service modules
│   │   ├── assistant_registry.py
=======
│   ├── services/            # Contains service modules
>>>>>>> 2cf0cdd2b47b630ac2959e0306bf0ccbed67e10b
│   │   ├── logger.py
│   │   ├── schemas.py
│   │   ├── tool_registry.py
│   ├── utils/               # Contains utility modules
<<<<<<< HEAD
│   │   ├── actions_for_assistants/ 
│   │   │   ├── prompts/
│   │   │   └── actions_for_assistants.py
│   │   ├── prompts_for_summarization/
│   │   ├── tests/ 
│   │   ├── allowed_file_extensions.py # The allowed file extensions 
│   │   ├── auth.py # The auth config.
│   │   ├── document_loaders_summarization.py # The document loaders used for summarization
│   │   └── document_loaders.py # The document loaders used for handling a list of documents
=======
│   │   ├── auth.py
>>>>>>> 2cf0cdd2b47b630ac2959e0306bf0ccbed67e10b
│   ├── .env.sample              # Contains the required env variables (CREATE AN .env file using it)
│   ├── main.py              # Main entry point for the application
├── Dockerfile               # Dockerfile for containerizing the application
├── requirements.txt         # Python dependencies 
├── app.yaml                 # Application configuration file
├── load_env.sh              # Loads env variables
├── local-start.sh           # Starts the local server
<<<<<<< HEAD
├── code-of-conduct.md          # Code of conduct for contributors
├── contribution.md           # Contribution guidelines
=======
>>>>>>> 2cf0cdd2b47b630ac2959e0306bf0ccbed67e10b
└── README.md                # Documentation file
```

## Installation:

### Navigate to the app directory

```bash
cd marvel-ai-backend/app
```

### Create and activate Virtual Environment

```bash
python -m venv env
source env/bin/activate
```

### Install Required Libraries
```bash
pip install -r requirements.txt
```

## Running Locally and Testing

## Prerequisites

- A Google Cloud account.
- Access to the Google Cloud Platform console.

## Steps for Authentication Setup

### Step 1: Create a Google Cloud Project

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.

### Step 2: Enable the Google Cloud APIs

1. Enable the following APIs:
   - VertexAI

### Step 3: Create a new AI Studio API Key

1. Navigate to the [AI Studio API Key page](https://aistudio.google.com/app/u/1/apikey) and create a new API key. This will connect with your Google Cloud Project.

### Step 4: Create a new .env and store the API Key

1. Create a new file called `.env` in the root of the project.
2. Copy the contents of the `.env.example` file into the `.env` file.
3. Replace the placeholder values with your API key and project ID.
4. Set the `ENV_TYPE` variable to `dev`.

### Step 5: Run the Application with Local Shell Script

1. Run the following command to start the application:

```bash
./local-start.sh
```
### Step 6: Set the API Header
1. Set the api-header to `dev`.
2. Send the request payload to whichever endpoint you want to test!

# Docker Setup Guide

## Overview

This guide is designed to help contributors set up and run the backend service using Docker. Follow these steps to ensure that your development environment is configured correctly.

## Prerequisites for Docker

Before you start, ensure you have the following installed:

- Docker
- Python

## Installation Instructions

### Step 1: Build the Docker Image

Navigate to the project's root directory and build the Docker image. Typically, this is done with the following command:

```Bash
docker build -t <image_name> .
```

### Step 2: Run the Docker Container

Run the Docker container using the following command:

```bash
docker run -p 8000:8000 <image_name>
```

This command starts a detached container that maps port 8000 of the container to port 8000 on the host.

## Environment Variables

The Docker container uses several key environment variables:

- ENV_TYPE set to "dev" for development.
- PROJECT_ID specifies your Google Cloud project ID.
- It is possible to enable LangChain tracing by setting the following environment variables. More information can be found on LangSmith
  `LANGCHAIN_TRACING_V2`
  `LANGCHAIN_ENDPOINT`
  `LANGCHAIN_API_KEY`
  `LANGCHAIN_PROJECT`
- Ensure these variables are correctly configured in a .env file.

## Accessing the Application

You can access the backend by visiting:

```Bash
http://localhost:8000/docs
```

After your container starts, you should see the FastAPI landing page, indicating that the application is running successfully.
