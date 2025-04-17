from typing import List, Literal
import uuid
from pydantic import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from app.api.error_utilities import ImageGenerationError
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
    



class ImageGenerator:
    def __init__(self,  args, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-2.0-flash-001"),
            "parser": JsonOutputParser(pydantic_object=ImageGenerationOutput),
           # "prompt": read_text_file("prompt/image-generator-prompt.txt"),
            "prompt_enhancement": read_text_file("prompt/prompt-for-enhancement.txt")
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
        self.safety_check_prompt = read_text_file("prompt/safety_prompt.txt")
        self.safety_check_parser = JsonOutputParser(pydantic_object=SafetyCheckOutput)

    def enhance_prompt(self) -> str:
        """Enhances the base prompt with educational context"""
        try:

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
        except Exception as e:
            logger.error(f"Failed to enhance prompt: {str(e)}")
            raise ValueError(f"Prompt enhancement failed: {str(e)}")

    def safety_check(self, prompt: str) -> bool:
        """
        Pre-generation safety check for prompt appropriateness using a dual-filter system:
        1. Keyword-based filtering
        2. AI-based content analysis using Gemini
        
        Args:
            prompt (str): The prompt to check
            
        Returns:
            SafetyCheckOutput: Safety check results
            
        Raises:
            ValueError: If safety check fails
        """
        try:
            # Step 1: Keyword-based filtering         
            
            # Convert prompt to lowercase for case-insensitive matching
            prompt_lower = prompt.lower()
            
            # Check for blocked keywords
            found_keywords = []
            for keyword in unsafe_keywords:
                if keyword in prompt_lower.split():
                    found_keywords.append(keyword)
                    
            if len(found_keywords) > 0:
                logger.warning(f"Blocked keywords found in prompt: {found_keywords}")

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
            logger.info(f"AI analysis complete")    
            return analysis

        except Exception as e:
            logger.error(f"Safety check failed: {str(e)}")
            raise ValueError(f"Safety check failed: {str(e)}")
        
    def save_to_cloud_storage(self, generated_image):
        """Save the image to Google Cloud Storage"""
        firebase_manager = FirebaseManager()
        image_url = firebase_manager.upload_image(generated_image, f"images/{uuid.uuid4()}.png")        
        logger.info(f"Image uploaded to Firebase: {image_url}")
        return image_url
    
    def generate_image(self):
        """Main image generation pipeline

        Returns:
            Dict containing image URL and enhanced prompt

        Raises:
            ImageGenerationError: If image generation fails
        """
        
        
        try:
            #  Enhance prompt with educational context
            enhanced_prompt = self.enhance_prompt()
            #if the prompt is not safe, return an error with details
            if not enhanced_prompt or  enhanced_prompt["is_safe"] == False:
                logger.error(f"Failed to enhance prompt: {enhanced_prompt['is_safe']}")
                return {
                    "error": "Content safety check failed during enhancement",
                    "details": enhanced_prompt.get('image_prompt', ''),
                    "is_safe": False
                }
                                              

            image_prompt =  enhanced_prompt.get('image_prompt')

            #  Perform Safety check on the enhanced prompt
            safety_check_analysis = self.safety_check(image_prompt)
            # If the prompt is not safe, return an error with details
            if not safety_check_analysis['is_safe']:
                logger.error(f"Content safety check failed - prompt contains inappropriate content")
                return {
                    "error": "Content safety check failed - prompt contains inappropriate content",
                    "details": safety_check_analysis['details']['assessment_explanation']
                }

          
            print("image_prompt",image_prompt)
            # Generate image
            response = self.image_generator_model.generate_images(
            prompt=image_prompt,
            # Optional:
            safety_filter_level="block_most",
            number_of_images=1,
            seed=0,
            add_watermark=False,
            )     
            if not response.images:
                logger.warning("Image generation returned no images, likely due to safety filters")
                raise ImageGenerationError("No images returned from generation API")
            
            generated_image = response.images[0]
            logger.info("Image generated successfully")
            generated_image.save("generated_image.png")
            # Upload to cloud storage
            try:
                image_url = self.save_to_cloud_storage(generated_image)
                return {
                    "image_url": image_url,
                    "enhanced_prompt": image_prompt
                }
            except Exception as e:
                logger.error(f"Failed to save image to cloud storage: {str(e)}", exc_info=True)
                raise ImageGenerationError(f"Image generated but storage failed: {str(e)}")          
                                    
                    
        except ValueError as e:
            logger.error(f"Image generation failed: {str(e)}")
            raise ValueError(f"Image generation failed: {str(e)}")    
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            raise ImageGenerationError(f"Image generation failed: {str(e)}")
        

class SafetyAssessmentDetails(BaseModel):
    detected_keywords: List[str] = Field(
        description="List of potentially concerning keywords found in the prompt"
    )    
    severity_score: int = Field(
        description="Score (1-5) "
    )
    educational_appropriateness_score: int = Field(
        description="Score (1-5) "
    )
    safety_assessment: Literal["Safe and Appropriate", 
                             "Potentially Problematic (Review)", 
                             "Unsafe or Inappropriate (Block)"] = Field(
        description="Overall safety and educational appropriateness assessment"
    )
    assessment_explanation: str = Field(
        description="Detailed reasoning for the assessment within the educational context"
    )

class SafetyCheckOutput(BaseModel):
    is_safe: bool = Field(description="Whether the prompt is safe for educational use")
    details: SafetyAssessmentDetails = Field(description="Detailed safety assessment information")          
