import os
import json
from app.services.logger import setup_logger
from together import Together
import base64
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from typing import List, Dict
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

logger = setup_logger(__name__)
client = Together()

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()


class ImageGenerator:
    def __init__(self):
        self.client = Together()
        self.config = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "width": 1024,
            "height": 768,
            "steps": 4,  # FLUX.1-schnell is optimized for low steps
            "n": 1
        }
        self._ensure_output_directory()

    def generate_single_image(self, input_data: Dict) -> Dict:
        """Generate a single image using FLUX.1-schnell model"""
        prompt = input_data["prompt"]
        slide_title = input_data["title"]
        
        try:
            response = self.client.images.generate(
                prompt=prompt,
                model=self.config["model"],
                width=self.config["width"],
                height=self.config["height"],
                steps=self.config["steps"],
                n=self.config["n"],
                response_format="b64_json"
            )
            
            image_data = response.data[0].b64_json
            image_path = self._save_image_to_disk(image_data, slide_title)
            
            logger.info(f"Successfully generated image for: {slide_title}")
            return {
                "title": slide_title,
                "image_path": image_path,
                "status": "success",
                "prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Failed to generate image for {slide_title}: {str(e)}")
            return {
                "title": slide_title,
                "error": str(e),
                "status": "failed",
                "prompt": prompt
            }

    def _ensure_output_directory(self) -> str:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Create 'generated_images' directory if it doesn't exist
        output_dir = os.path.join(script_dir, 'generated_images')
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _save_image_to_disk(self, image_data: str, slide_title: str) -> str:
        output_dir = self._ensure_output_directory()
        safe_title = "".join(x for x in slide_title if x.isalnum() or x in "_ -").rstrip()
        filename = f"{safe_title}.png"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(image_data))
        
        logger.info(f"Saved image to: {file_path}")
        return file_path

class ImagePromptGenerator:
    def __init__(self, verbose=False):
        try:
            default_config = {
                "model": GoogleGenerativeAI(model="gemini-1.5-pro"),
                "prompt": read_text_file("prompt/visual_prompt.txt"),
                "theme_prompt": read_text_file("prompt/theme_prompt.txt")
            }
            self.prompt = default_config["prompt"]
            self.model = default_config["model"]
            self.theme_prompt = default_config["theme_prompt"]
            
            if not self.prompt:
                raise ValueError("Failed to load prompt template from file")
                
            logger.info("Successfully initialized ImagePromptGenerator")
        except Exception as e:
            logger.error(f"Error initializing ImagePromptGenerator: {str(e)}")
            raise

    def generate_image_prompt(self, slides_data: List[dict]):
        try:
            if not slides_data:
                raise ValueError("Slides data cannot be empty")

            # Generate theme once using the first slide's title
            parser = PydanticOutputParser(pydantic_object=ThemeOutput)
            
            theme_prompt = PromptTemplate(
                template=self.theme_prompt + "\n{format_instructions}",
                input_variables=["title"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            
            # Access the title correctly from the first slide
            first_slide_title = slides_data[0].get("title", "")  # Using .get() for safety
            theme = theme_prompt | self.model | parser
            theme_result = theme.invoke({"title": first_slide_title})
            logger.info(f"Generated theme based on first slide: {theme_result.theme}")

            # Create prompt templates for different aspects
            visual_prompt_parser = PydanticOutputParser(pydantic_object=VisualPromptOutput)
            
            visual_prompt = PromptTemplate(
                template=self.prompt + "\n{format_instructions}",
                input_variables=["title", "content", "theme"],
                partial_variables={"format_instructions": visual_prompt_parser.get_format_instructions()}
            )
            
            # composition_prompt_parser = PydanticOutputParser(pydantic_object=CompositionOutput)
            
            composition_prompt = PromptTemplate(
                template="Suggest composition for slide with layout {template} and title '{title}'"
                "",
                input_variables=["template", "title"]
                # partial_variables={"format_instructions": composition_prompt_parser.get_format_instructions()}
            )

            # Create parallel chain for processing each slide
            slide_chain = RunnableParallel(
                visual_description=(visual_prompt | self.model | visual_prompt_parser),
                composition=(composition_prompt | self.model)
            )

            # Process all slides in parallel using batch, including the theme
            results = slide_chain.batch([
                {
                    "title": slide.get("title", ""),
                    "content": slide.get("content", "") if isinstance(slide.get("content"), str) 
                             else " ".join(slide.get("content", [])),  # Handle both string and list content
                    "template": slide.get("template", "default"),
                    "theme": theme_result
                }
                for slide in slides_data
            ])

            # Combine the parallel results into final prompts
            final_prompts = {}
            for i, slide in enumerate(slides_data):
                result = results[i]
                final_prompts[slide["title"]] = (
                    f"{result['visual_description']}."
                    f"{theme_result}. "
                    # f"Composition: {result['composition']}"
                )
                logger.info(f"Generated prompt for slide: {slide['title']}\n\n\n{result['visual_description']}\n\n\n{theme_result}")

            # logger.info(f"Generated promptS: {final_prompts}")
            return final_prompts

        except Exception as e:
            logger.error(f"Error in generate_image_prompt: {str(e)}")
            raise

def create_image_generation_chain(prompts: Dict[str, str]):
    """Create a parallel chain for image generation using FLUX.1-schnell"""
    image_generator = ImageGenerator()
    
    tasks = {
        f"image_{i}": RunnableLambda(lambda x, prompt=prompt, title=title: 
            image_generator.generate_single_image({
                "prompt": prompt,
                "title": title
            })
        )
        for i, (title, prompt) in enumerate(prompts.items())
    }
    
    return RunnableParallel(tasks)

def image_generation_handler(image_generator_args):
    try:
        slides_data = image_generator_args.presentation_content
        
        # Generate prompts
        prompt_generator = ImagePromptGenerator()
        prompts = prompt_generator.generate_image_prompt(slides_data)
        
        # Save prompts for debugging
        save_to_file(prompts, "image_prompts.json")
        logger.info(f"Generated prompts for {len(prompts)} slides")

        # Create and execute the parallel image generation chain
        image_chain = create_image_generation_chain(prompts)
        results = image_chain.invoke({})
        
        # Process and validate results
        processed_results = []
        for key, result in results.items():
            if result["status"] == "success":
                processed_results.append({
                    "title": result["title"],
                    "image_path": result["image_path"],
                    "prompt": result["prompt"]
                })
            else:
                logger.error(f"Failed to generate image for {result['title']}: {result.get('error')}")
                
        logger.info(f"Successfully generated {len(processed_results)} images")
        return processed_results
        
    except Exception as e:
        logger.error(f"Error in image_generation_handler: {e}")
        raise

async def async_image_generation_handler(image_generator_args):
    try:
        slides_data = image_generator_args.presentation_content
        prompt_generator = ImagePromptGenerator()
        prompts = prompt_generator.generate_image_prompt(slides_data)
        
        image_chain = create_image_generation_chain(prompts)
        results = await image_chain.ainvoke({})
        
        processed_results = []
        for key, result in results.items():
            if result["status"] == "success":
                processed_results.append({
                    "title": result["title"],
                    "image_path": result["image_path"],
                    "prompt": result["prompt"]
                })
            
        logger.info(f"Successfully generated {len(processed_results)} images")
        return processed_results
        
    except Exception as e:
        logger.error(f"Error in async_image_generation_handler: {e}")
        raise

def save_to_file(data: Dict, filename: str) -> None:
    """
    Save dictionary data to a JSON file in the 'generated_prompts' directory.
    
    Args:
        data (Dict): The dictionary data to save
        filename (str): Name of the file to save to
    """
    try:
        # Get the directory containing the script file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create 'generated_prompts' directory if it doesn't exist
        output_dir = os.path.join(script_dir, 'generated_prompts')
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the full file path
        file_path = os.path.join(output_dir, filename)
        
        # Save the data to JSON file with proper formatting
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully saved prompts to: {file_path}")
        
    except Exception as e:
        logger.error(f"Error saving prompts to file: {str(e)}")
        raise



class ThemeOutput(BaseModel):
    theme: str = Field(description="A single line description of the presentation theme (e.g., 'Futuristic Innovation and Discovery')")

class VisualPromptOutput(BaseModel):
    visual_description: str = Field(description="A simple yetdetailed prompt for generating an image that matches the slide content and theme")

# class CompositionOutput(BaseModel):
#     composition: str = Field(description="A description of the suggested composition and layout for the slide")




    # call get_image_prompt
    # prompt_generator = ImagePromptGenerator()
    # prompts = prompt_generator.generate_image_prompt(image_generator_args)
    # call get_dimensions (slide_gen use case)
    # dimensions = get_dimensions()
    # # initialize image generator with dimensions
    # image_generator = ImageGenerator(prompts, dimensions)
    # # call get_image
    # b4_image = image_generator.generate_image()
    # # save image to local
    # image_generator.save_image(b4_image)
    # # save image to firebase and get image URL
    # firebase_url = image_generator.upload_to_firebase()
    # return firebase_url
