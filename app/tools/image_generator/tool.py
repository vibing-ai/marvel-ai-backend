import uuid
from pydantic import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
import vertexai
import os
from app.services.logger import setup_logger
from app.tools.image_generator.utils import unsafe_keywords
from app.tools.presentation_generator_updated.slide_generator.firebase import FirebaseManager

logger = setup_logger(__name__)

#from langchain_google_vertexai.vision_models import VertexAIImageGeneratorChat, ImageGenerationModel
from vertexai.preview.vision_models import ImageGenerationModel

from app.services.logger import setup_logger

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()
    
class ImageGenerationOutput(BaseModel):
    image_prompt: str = Field(description="The image prompt")
    is_safe: bool = Field(description="Whether the prompt is safe for educational use")
    

class SafetyCheckOutput(BaseModel):
    is_safe: bool = Field(description="Whether the prompt is safe for educational use")
    details: dict = Field(description="Details about the safety check")


class ImageGenerator:
    def __init__(self,  args, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-2.0-flash-001"),
            "parser": JsonOutputParser(pydantic_object=ImageGenerationOutput),
           # "prompt": read_text_file("prompt/image-generator-prompt.txt"),
            "prompt_enhancement": read_text_file("prompt/prompt-enhancement.txt")
        }
        self.args = args
        self.verbose = verbose
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.image_generator_model  = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        self.prompt = prompt or default_config["prompt_enhancement"]
        self.system_prompt = read_text_file("prompt/system_instruction_prompt.txt")
        formatted_presets = ""
        if  self.args.presets:
            for key, values in self.args.presets.items():
                formatted_presets += f"{key}- {values}\n"
                self.presets = formatted_presets
        else:
            self.presets = None
        self.safety_check_prompt = read_text_file("prompt/new.txt")
        self.safety_check_parser = JsonOutputParser(pydantic_object=SafetyCheckOutput)

    def enhance_prompt(self) -> str:
        """Enhances the base prompt with educational context"""

        prompt = PromptTemplate(
            template=self.system_prompt + self.prompt,
            input_variables=["prompt", "grade_level", "subject","presets"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        input_parameters = {
            "prompt": self.args.prompt,
            "grade_level": self.args.grade_level,
            "subject": self.args.subject,
            "presets": self.presets
        }
        
        chain =  prompt | self.model | self.parser
        enhanced = chain.invoke(input_parameters)       
        
        if self.verbose:
            logger.info(f"Enhanced prompt: {enhanced}")#{"image_prompt":str})
            
        return enhanced
    def safety_check(self, prompt: str) -> bool:
        """
        Pre-generation safety check for prompt appropriateness using a dual-filter system:
        1. Keyword-based filtering
        2. AI-based content analysis using Gemini
        
        Args:
            prompt (str): The prompt to check
            
        Returns:
            bool: True if prompt passes safety checks, False otherwise
            
        Raises:
            ValueError: If prompt contains explicitly inappropriate content
        """
        try:
            # Step 1: Keyword-based filtering
            
            
            # Convert prompt to lowercase for case-insensitive matching
            prompt_lower = prompt.lower()
            logger.info(f"Prompt Lower: {prompt_lower}")
            
            # Check for blocked keywords
            found_keywords = []
            for keyword in unsafe_keywords:
                if keyword in prompt_lower.split():
                    found_keywords.append(keyword)
                    
            #found_keywords = [word for word in unsafe_keywords if word in prompt_lower.split()]
            if len(found_keywords) > 0:
                logger.warning(f"Blocked keywords found in prompt: {found_keywords}")
                #return False

            # Step 2: AI-based content analysis using Gemini
           
            
            safety_check_prompt = PromptTemplate(
                template=self.safety_check_prompt,
                input_variables=["prompt","found_keywords"],
                partial_variables={"format_instructions": self.safety_check_parser.get_format_instructions()}
            )
            input_parameters = {
                "enhanced_prompt": prompt,
                "found_keywords": found_keywords,
                "original_user_prompt": self.args.prompt,
                "subject": self.args.subject,
                "instructional_level": self.args.grade_level,
                "style_preset": self.presets

            }
          
            chain =  safety_check_prompt | self.model | self.safety_check_parser
            
            # Get AI analysis
            analysis = chain.invoke(input_parameters)
            logger.info(f"AI analysis: {analysis}")         
           
            
            if not analysis.get("is_safe", False):
                logger.warning(f"AI safety check failed: {analysis.get('details', 'Unknown reason')}")
                return False
                
            # if not analysis.get("educational_value", False):
            #     logger.warning("Content lacks educational value")
            #     return False

            logger.info("Prompt passed safety checks")
            return True

        except Exception as e:
            logger.error(f"Error in safety check: {str(e)}")
            # Fail closed - if there's an error, reject the prompt
            return False
        
    def generate_image(self):
        """Main image generation pipeline"""
        try:
            # Step 1: Enhance prompt with educational context
            enhanced_prompt = self.enhance_prompt()
            if not enhanced_prompt or  enhanced_prompt["is_safe"] == False:
                logger.error(f"Failed to enhance prompt: {enhanced_prompt['is_safe']}")
                return {
                    "error": "Failed to generate a valid enhanced prompt"
                }                               

            image_prompt = enhanced_prompt.image_prompt if hasattr(enhanced_prompt, 'image_prompt') else enhanced_prompt.get('image_prompt')
            logger.info(f"prompt: {image_prompt}")
             #  Safety check
            if not self.safety_check(image_prompt):
                logger.error(f"Content safety check failed - prompt contains inappropriate content")
                return {
                    "error": "Content safety check failed - prompt contains inappropriate content"
                }

            try:

                response = self.image_generator_model.generate_images(
                
                prompt=image_prompt,
                negative_prompt="",
                safety_filter_level="block_most",
                # Optional:
                number_of_images=1,
                seed=0,
                add_watermark=False,
            )
            except Exception as e:
                logger.error(f"Image generation failed: {str(e)}")
                
            if response.images:
              generated_image = response.images[0]
              generated_image.save("generated_image.png")
            else:
                generated_image = None
            logger.info(f"Generated image ")
           
            # update the image to database using uuid for image name
            firebase_manager = FirebaseManager()
            if generated_image:
                image_url = firebase_manager.upload_image(generated_image, f"images/{uuid.uuid4()}.png")
            else:
                image_url = None

            logger.info(f"Image uploaded to Firebase: {image_url}")
            #result = Output(image_url=image_url, enhanced_prompt=image_prompt)
            return {
                "image_url": image_url,
                "enhanced_prompt": image_prompt
            }
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            
class Output(BaseModel):
    image_url: str = Field(..., description="URL of the generated image")
    enhanced_prompt: str = Field(..., description="Enhanced prompt used for generation")
            
    #         # Step 2: Safety check
    #         if not self.safety_check(enhanced_prompt):
    #             raise ValueError("Prompt failed safety check")
                
    #         # Step 3: Configure generation parameters
    #         generation_params = {
    #             "prompt": enhanced_prompt,
    #             "model": "vertex-ai-image",  # Use actual Vertex AI model name
    #             "safety_settings": "HIGH",
    #             "style": self.args.style or "educational",
    #             "aspect_ratio": "4:3"  # Standard educational format
    #         }
    #     logger.info(f'Generating image for slide {slide} with prompt')
    #     model = self.generator
             
    #     prompt = f'Generate an image with {slide_data["image_prompt"]}.'
    #     #aspect_ratio = '16:9" if slide_data["template"] in ["titleAndBody", "sectionHeader"] else "4:3"
    #     response = model.generate_images(
    #         prompt=prompt,
    #         # Optional:
    #         number_of_images=1,
    #         seed=0,
    #         aspect_ratio="16:9"if slide_data["template"] in ["titleAndBody", "sectionHeader"] else "4:3",
    #         add_watermark=False,
    #     )
    #    # response= {"images": [None]}

    #     if response.images:
    #         generated_image = response.images[0]
    #         logger.info(f"Generated image for slide {slide}")
    #         logger.info(f"generated parameters: {generated_image._generation_parameters}")

            
    #        # Get image dimensions
    #         try:
    #             # Convert to PIL Image first
    #             image_bytes = generated_image._image_bytes
    #             pil_image = Image.open(io.BytesIO(image_bytes))
    #             width, height = pil_image.size
    #             logger.info(f'Generated image resolution: {width}x{height} for slide template {slide_data["template"]}')
    #         except Exception as e:
    #             logger.error(f"Failed to get image dimensions: {e}")
    #             width, height = None, None
    #         return generated_image
     
    #     else:
    #         logger.error("No images were generated.")
    #     return None


       


# class ImageGeneratorResponse(BaseModel):
#     """Response model for generated images"""
#     image_url: str = Field(..., description="URL of the generated image")
#     enhanced_prompt: str = Field(..., description="Enhanced prompt used for generation")
#     metadata: dict = Field(default_factory=dict, description="Additional metadata about the generation")

# class ImageGenerator:
#     def __init__(self):
#         """Initialize the image generator with configuration"""
#         #self.config = config
#         self.api_key = os.getenv("GOOGLE_API_KEY")
#         self.client = genai.Client(api_key=self.api_key)
#         self.bucket_name = os.getenv('GCS_BUCKET_NAME')
#         self.storage_client = storage.Client()
        
#         # Create local directory for temporary image storage
#         self.image_dir = os.path.join(os.path.dirname(__file__), "generated_images")
#         os.makedirs(self.image_dir, exist_ok=True)

#     def enhance_prompt(self, args) -> str:
#         """Enhance the prompt with additional context"""
#         prompt_parts = [args.prompt]
        
#         if args.subject:
#             prompt_parts.append(f"Subject: {args.subject}")
#         if args.grade_level:
#             prompt_parts.append(f"Grade Level: {args.grade_level}")
#         if args.style:
#             prompt_parts.append(f"Style: {args.style}")
            
#         return ". ".join(prompt_parts)

#     def generate_image(self, args) -> ImageGeneratorResponse:
#         """Generate image using Google's Imagen model"""
#         try:
#             enhanced_prompt = self.enhance_prompt(args)
#             logger.info(f"Generating image with prompt: {enhanced_prompt}")

#             response = self.client.models.generate_images(
#                 model="imagen-3.0-generate-002",
#                 prompt=enhanced_prompt,
#                 config=types.GenerateImagesConfig(
#                     number_of_images=1,
#                 )
#             )

#             # Generate unique filename
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             clean_title = re.sub(r'[^\w\-_\.]', '_', args.prompt[:30])
#             filename = f"{timestamp}_{clean_title}.png"

#             # Process the generated image
#             for generated_image in response.generated_images:
#                 image_bytes = generated_image.image.image_bytes
                
#                 # Save to Cloud Storage
#                 image_url = self.save_to_cloud_storage(image_bytes, filename)
                
#                 # Create response
#                 return ImageGeneratorResponse(
#                     image_url=image_url,
#                     enhanced_prompt=enhanced_prompt,
#                     metadata={
#                         "timestamp": timestamp,
#                         "size": args.size,
#                         "filename": filename
#                     }
#                 )

#         except Exception as e:
#             logger.error(f"Error generating image: {str(e)}")
#             raise

#     def save_to_cloud_storage(self, image_bytes: bytes, filename: str) -> str:
#         """Save image to Google Cloud Storage and return public URL"""
#         try:
#             bucket = self.storage_client.bucket(self.bucket_name)
#             blob = bucket.blob(f"generated_images/{filename}")
            
#             blob.upload_from_string(
#                 image_bytes,
#                 content_type='image/png'
#             )
            
#             # Make the blob publicly accessible
#             blob.make_public()
            
#             logger.info(f"Image uploaded to GCS: {blob.public_url}")
#             return blob.public_url
            
#         except Exception as e:
#             logger.error(f"Failed to upload image to cloud storage: {str(e)}")
#             raise

#     def save_locally(self, image_bytes: bytes, filename: str) -> str:
#         """Save image locally and return file path"""
#         try:
#             file_path = os.path.join(self.image_dir, filename)
            
#             with open(file_path, 'wb') as f:
#                 f.write(image_bytes)
            
#             logger.info(f"Image saved locally at: {file_path}")
#             return file_path
            
#         except Exception as e:
#             logger.error(f"Failed to save image locally: {str(e)}")
#             raise