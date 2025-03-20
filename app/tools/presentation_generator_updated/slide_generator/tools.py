from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any
import os
from app.services.logger import setup_logger
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from google.cloud import storage
from dotenv import load_dotenv
import requests
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request  # Correct import

# Load environment variables from app/.env
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
load_dotenv(env_path)
logger = setup_logger(__name__)
api_key = os.getenv('GOOGLE_API_KEY')
logger.info(f"Loaded GOOGLE_API_KEY: {api_key[:5] if api_key else 'None'}...")
logger.info(f"Loaded PROJECT_ID: {os.getenv('PROJECT_ID')}")

def read_text_file(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_file_path = os.path.join(script_dir, file_path)
    with open(absolute_file_path, 'r') as file:
        return file.read()

def generate_image_with_imagen3(slide_title: str, content: Union[str, list, dict, Any], template: str) -> str:
    """Generate an image using Imagen 3 and store it in Google Cloud Storage."""
    if isinstance(content, str):
        content_str = content
    elif isinstance(content, list):
        content_str = " ".join(content)
    elif isinstance(content, dict):
        flat_content = []
        for value in content.values():
            if isinstance(value, dict):
                flat_content.append(" ".join(value.values()))
            else:
                flat_content.append(str(value))
        content_str = " ".join(flat_content)
    else:
        content_str = str(content)
    prompt = f"An infographic-style illustration for '{slide_title}'. Include elements like {content_str}. Minimalist and clean, suitable for an educational presentation."
    
    layout_prompts = {
        "titleAndBody": "Centered illustration with labels.",
        "titleAndBullets": "Infographic with icons and keywords.",
        "twoColumn": "Split image showing contrasting ideas.",
        "sectionHeader": "Hero image with minimal text overlay."
    }
    prompt += f" {layout_prompts.get(template, 'Infographic-style illustration.')}"
    
    dimensions = {
        "titleAndBody": {"width": 1280, "height": 720},
        "titleAndBullets": {"width": 1024, "height": 768},
        "twoColumn": {"width": 800, "height": 600},
        "sectionHeader": {"width": 1600, "height": 900}
    }
    dims = dimensions.get(template, {"width": 1024, "height": 768})

    # OAuth authentication
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    # Refresh credentials if needed
    if not credentials.valid:
        credentials.refresh(Request())
    token = credentials.token
    project_id = os.getenv("PROJECT_ID")
    endpoint = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/imagegeneration@006:predict"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "width": dims["width"],
            "height": dims["height"]
        }
    }
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        image_data = base64.b64decode(response.json()["predictions"][0]["bytesBase64Encoded"])
    except requests.RequestException as e:
        logger.error(f"Failed to generate image with Imagen 3: {e}")
        return None

    client = storage.Client(project=project_id)
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"slides/{os.urandom(16).hex()}.jpg")
    blob.upload_from_string(image_data, content_type="image/jpeg")
    logger.info(f"Image uploaded to {blob.public_url}")
    return blob.public_url

class SlideGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=SlidePresentation),
            "prompt": read_text_file("prompt/slide_generator_prompt.txt"),
            "vectorstore_class": Chroma
        }
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose
        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")

    def validate_slides_content(self, response, topic):
        topic_keywords = set(topic.lower().split())
        topic_coverage = 0
        garbage_coverage = 0
        template_requirements_met = False
        slides = response["slides"]
        try:
            if len(slides) == 0:
                raise ValueError("No slides found in the response")
            for slide in slides:
                slide_text = ""
                if slide["template"] == "twoColumn":
                    template_requirements_met = True
                if isinstance(slide["content"], list):
                    slide_text = ' '.join(slide["content"])
                elif isinstance(slide["content"], dict):
                    flat_content = []
                    for value in slide["content"].values():
                        if isinstance(value, dict):
                            flat_content.append(" ".join(value.values()))
                        else:
                            flat_content.append(str(value))
                    slide_text = ' '.join(flat_content)
                else:
                    slide_text = slide["content"]
                if any(keyword in slide_text.lower() for keyword in topic_keywords):
                    topic_coverage += 1
                if any(char in slide_text for char in ['*', '\n', '`', '_']):
                    garbage_coverage += 1
            coverage_percentage = (topic_coverage / len(slides)) * 100
            garbage_coverage_percentage = (garbage_coverage / len(slides)) * 100
            return {
                "topic_coverage": coverage_percentage,
                "template_requirements_met": template_requirements_met,
                "garbage_coverage_percentage": garbage_coverage_percentage,
                "valid": coverage_percentage > 70 and template_requirements_met and garbage_coverage_percentage == 0
            }
        except ValueError as e:
            raise ValueError(e)

    def compile_context(self):
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["instructional_level", "topic", "slides_titles"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        chain = prompt | self.model | self.parser
        logger.info(f"Chain compilation complete")
        return chain

    def generate_slides(self):
        logger.info(f"Creating the Slides for the Presentation")
        chain = self.compile_context()
        input_parameters = {
            "instructional_level": self.args.instructional_level,
            "topic": self.args.topic,
            "slides_titles": self.args.slides_titles,
            "lang": self.args.lang
        }
        logger.info(f"Input parameters: {input_parameters}")
        response = chain.invoke(input_parameters)
        logger.info(f"Generated response: {response}")

        for slide in response["slides"]:
            image_url = generate_image_with_imagen3(slide["title"], slide["content"], slide["template"])
            slide["image_url"] = image_url if image_url else "Image generation failed"

        validation_results = self.validate_slides_content(response=response, topic=self.args.topic)
        logger.info(f"Response validation: {validation_results}")
        if not validation_results["valid"]:
            logger.warning(f"Generated content may not fully match the requested topic")
        return response

class Slide(BaseModel):
    title: str = Field(..., description="The title of the slide")
    template: str = Field(..., description="The slide template type: sectionHeader, titleAndBody, titleAndBullets, twoColumn")
    content: str | list | dict | Any = Field(None, description="Content of the slide, can be string, list, dict, or any type")
    image_url: Optional[str] = Field(None, description="URL of the generated image for the slide")

class SlidePresentation(BaseModel):
    slides: List[Slide] = Field(..., description="The complete set of slides in the presentation")