import re
import json
import hashlib
import time
from typing import List, Dict
from functools import lru_cache
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnableLambda  
from langchain_google_genai import GoogleGenerativeAI
import langsmith as ls
from langsmith import trace
from fastapi import HTTPException
from app.services.logger import setup_logger
from app.services.schemas import SyllabusGeneratorArgsModel
from app.tools.syllabus_generator.schemas import (
    CourseInformation, CourseDescriptionObjectives, CourseContentItem,
    PoliciesProcedures, AssessmentGradingCriteria, LearningResource,
    CourseScheduleItem, SyllabusSchema
)

logger = setup_logger(__name__)

class SyllabusRequestArgs:
    """Class to structure the input arguments for generating a syllabus."""
    def __init__(self, syllabus_generator_args: SyllabusGeneratorArgsModel, summary: str):
        # Add default values for missing fields
        self._grade_level = syllabus_generator_args.grade_level or "Not specified"
        self._subject = syllabus_generator_args.subject or "Not specified"
        self._course_description = syllabus_generator_args.course_description or ""
        self._objectives = syllabus_generator_args.objectives or ""
        self._required_materials = syllabus_generator_args.required_materials or ""
        self._grading_policy = syllabus_generator_args.grading_policy or ""
        self._policies_expectations = syllabus_generator_args.policies_expectations or ""
        self._course_outline = syllabus_generator_args.course_outline or ""
        self._additional_notes = syllabus_generator_args.additional_notes or ""
        self._lang = syllabus_generator_args.lang or "en"
        self._summary = summary or ""

    def to_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "grade_level": self._grade_level,
            "subject": self._subject,
            "course_description": self._course_description,
            "objectives": self._objectives,
            "required_materials": self._required_materials,
            "grading_policy": self._grading_policy,
            "policies_expectations": self._policies_expectations,
            "course_outline": self._course_outline,
            "additional_notes": self._additional_notes,
            "lang": self._lang,
            "summary": self._summary,
        }
    
class PromptFactory:
    """Factory class to generate prompts for each section of the syllabus."""
    @staticmethod
    def course_information(parser_intructions: str) -> PromptTemplate:
        """Generate a detailed and structured course information prompt."""

        return PromptTemplate(
            template=(
                """
                You are an expert curriculum designer tasked with creating detailed course information in {lang}.
                # Context and Available Information
                Grade Level: {grade_level}
                Subject: {subject}
                Course Description: {course_description}
                Summary: {summary}
                Additional Notes: {additional_notes}
                # Instructions
                1. Generate a coherent and professional course title that reflects the subject and grade level
                2. If the grade level is not specified, infer it from other context
                3. Expand the course description to be comprehensive, even if minimal input is provided
                4. Use any available context to fill gaps in missing information
                5. Respond in {lang} language.
                {format_instructions}
                """
            ),
            input_variables=["grade_level", "subject", "course_description", "lang", "summary", "additional_notes"],
            partial_variables={"format_instructions": parser_intructions},
        )
    
    @staticmethod
    def course_description_objectives(parser_intructions: str) -> PromptTemplate:
        """Generate detailed course objectives and intended learning outcomes prompt."""

        return PromptTemplate(
            template=(
                """
                You are an expert in educational objectives and learning outcomes.
                
                # Context and Available Information
                Grade Level: {grade_level}
                Subject: {subject}
                Course Description: {course_description}
                Objectives: {objectives}
                Summary: {summary}
                
                # Instructions
                1. Create clear, measurable learning objectives aligned with Bloom's taxonomy
                2. If no objectives are provided, generate appropriate ones based on the subject and grade level
                3. Ensure objectives are specific and achievable within the course timeframe
                4. Include both knowledge and skill-based outcomes
                5. Respond in {lang} language.
                
                {format_instructions}
                """
            ),
            input_variables=["objectives", "lang", "summary", "grade_level", "subject", "course_description"],
            partial_variables={"format_instructions": parser_intructions},
        )
    
    @staticmethod
    def course_content(parser_intructions: str) -> PromptTemplate:
        """Generate a detailed course content outline prompt."""
        return PromptTemplate(
            template=(
                """
                You are an expert curriculum designer creating a detailed course content outline.
                
                # Context from Previous Generation Steps
                Course Title: {course_title}
                Grade Level: {grade_level}
                Course Description: {course_information}
                
                # Learning Objectives
                {objectives}
                
                # Additional Context
                Course Outline: {course_outline}
                Summary: {summary}
                
                # Instructions
                1. Create a logical sequence of course units based on the objectives and description
                2. If no course outline is provided, generate an appropriate one based on the subject and objectives
                3. Include appropriate time units (weeks, days, months) based on the course scope
                4. Each unit should build on previous knowledge and support the learning outcomes
                5. Respond in {lang} language.
                
                {format_instructions}
                """
            ),
            input_variables=["course_information", "course_outline", "lang", "summary", "objectives"],
            partial_variables={"format_instructions": parser_intructions},
        )
    
    @staticmethod
    def policies_procedures(parser_intructions: str) -> PromptTemplate:
        """Generate a prompt for drafting clear and professional course policies and procedures."""
        return PromptTemplate(
            template=(
                """
                You are an expert in educational policies creating clear guidelines for a course.
                
                # Course Context
                Course Title: {course_title}
                Grade Level: {grade_level}
                
                # Available Policy Information
                Grading Policy: {grading_policy}
                Class Policies and Expectations: {policies_expectations}
                
                # Instructions
                1. Create clear, fair, and comprehensive policies appropriate for the course level
                2. If specific policies aren't provided, generate standard ones appropriate for the grade level
                3. Include attendance requirements, late submission policies, and academic honesty guidelines
                4. Ensure policies align with typical educational standards for this level
                5. Respond in {lang} language.
                
                {format_instructions}
                """
            ),
            input_variables=["grading_policy", "policies_expectations", "lang", "grade_level", "course_title"],
            partial_variables={"format_instructions": parser_intructions},
        )
    
    @staticmethod
    def assessment_grading_criteria(parser_intructions: str) -> PromptTemplate:
        """Generate a prompt for defining assessment methods and grading criteria."""
        return PromptTemplate(
            template=(
                """
                You are an assessment specialist designing fair evaluation methods.
                
                # Course Context
                Course Title: {course_title}
                Grade Level: {grade_level}
                Learning Objectives: {objectives}
                
                # Available Assessment Information
                Grading Policy: {grading_policy}
                
                # Instructions
                1. Design assessment methods that align with the learning objectives
                2. If no grading policy is provided, create a balanced assessment strategy appropriate for the subject
                3. Include a variety of assessment types (exams, projects, participation)
                4. Provide a clear grading scale with percentage ranges
                5. Respond in {lang} language.
                
                {format_instructions}
                """
            ),
            input_variables=["grading_policy", "lang", "course_title", "grade_level", "objectives"],
            partial_variables={"format_instructions": parser_intructions},
        )
    
    @staticmethod
    def learning_resources(parser_intructions: str) -> PromptTemplate:
        """Generate a prompt for compiling a comprehensive list of recommended learning resources."""
        return PromptTemplate(
            template=(
                """
                You are an educational resource specialist recommending learning materials.
                
                # Course Context
                Course Title: {course_title}
                Subject: {subject}
                Grade Level: {grade_level}
                
                # Available Materials Information
                Required Materials: {required_materials}
                
                # Instructions
                1. Recommend appropriate learning resources for this course and grade level
                2. If no materials are specified, suggest standard resources for this subject
                3. Include a mix of textbooks, online resources, and supplementary materials
                4. Ensure resources are appropriate for the grade level and learning objectives
                5. Respond in {lang} language.
                
                {format_instructions}
                """
            ),
            input_variables=["required_materials", "lang", "course_title", "subject", "grade_level"],
            partial_variables={"format_instructions": parser_intructions},
        )
    
    @staticmethod
    def course_schedule(parser_intructions: str) -> PromptTemplate:
        """Generate a prompt for constructing a detailed course schedule."""
        return PromptTemplate(
            template=(
                """
                You are creating a detailed course schedule based on the course content.
                
                # Course Information
                Course Title: {course_title}
                Grade Level: {grade_level}

                # Course Content Structure
                {course_resumed_content}
                
                # Instructions
                1. Create a detailed schedule that follows the course content structure
                2. Match the unit_time format used in the course content (weeks, days, etc.)
                3. Include specific dates or time periods for each topic
                4. Add appropriate activities for each topic that support the learning objectives
                5. Respond in {lang} language.
                
                {format_instructions}
                """
            ),
            input_variables=["course_outline", "lang", "course_title", "grade_level", "course_resumed_content"],
            partial_variables={"format_instructions": parser_intructions},
        )

class LLMCache:
    """Simple cache for LLM responses to reduce redundant calls."""
    
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
    
    def _get_key(self, input_dict):
        """Create a deterministic hash from the input dictionary."""
        # Sort the dictionary to ensure consistent hashing
        serialized = json.dumps(input_dict, sort_keys=True)
        return hashlib.md5(serialized.encode()).hexdigest()
    
    def get(self, input_dict):
        """Retrieve cached result if available."""
        key = self._get_key(input_dict)
        return self.cache.get(key)
    
    def set(self, input_dict, result):
        """Cache the result."""
        key = self._get_key(input_dict)
        # Simple LRU implementation - clear cache if too large
        if len(self.cache) >= self.max_size:
            self.cache.clear()  
        self.cache[key] = result

class ParserFactory:
    """Factory class to create parsers for each section of the syllabus."""
    @staticmethod
    def create_parsers() -> Dict[str, JsonOutputParser]:
        
        return {
            "course_information": JsonOutputParser(pydantic_object=CourseInformation),
            "course_description_objectives": JsonOutputParser(pydantic_object=CourseDescriptionObjectives),
            "course_content": JsonOutputParser(pydantic_object=CourseContentItem),
            "policies_procedures": JsonOutputParser(pydantic_object=PoliciesProcedures),
            "assessment_grading_criteria": JsonOutputParser(pydantic_object=AssessmentGradingCriteria),
            "learning_resources": JsonOutputParser(pydantic_object=LearningResource),
            "course_schedule": JsonOutputParser(pydantic_object=CourseScheduleItem),
        }
    
class ChainBuilder:
    """Class to build a chain of prompts, model, and parsers for a section."""
    def __init__(self, model, parsers: Dict[str, JsonOutputParser], cache=None, verbose=False):
        self.model = model
        self.parsers = parsers
        self._cache = cache
        self.verbose = verbose
    
    def create_fallback(self, section_name: str) -> list[RunnableLambda]:
        """Create a fallback function for a section chain."""
        def section_fallback(input):
            error = str(input["error"]) if "error" in input else None
            logger.error(f"Failed to generate {section_name} section: {error}")
            return {
                "status": "failed",
                "error": error or f"Failed to generate {section_name} section.",
                "section": section_name,
                "fallback": True
            }
        return [RunnableLambda(section_fallback)]
    
    def build_chain_with_fallback(self, prompt: PromptTemplate, section_name: str, parser_key: str) -> Runnable:
        """Build a chain with a prompt, model, parser, and fallback."""
        parser = self.parsers[parser_key]
        chain = prompt | self.model | parser
        chain_with_fallback = chain.with_fallbacks(
            self.create_fallback(section_name), 
            exception_key="error"
        )
        return chain_with_fallback.with_config(run_name=section_name)

    def build_chain_with_cache_fallback(
            self, 
            prompt: PromptTemplate, 
            section_name: str, 
            parser_key: str) -> Runnable:
        """Build a chain with a prompt, model, parser, and caching and fallback."""

        chain_with_fallback = self.build_chain_with_fallback(prompt, section_name, parser_key)

        def cached_invoke(input_dict):
            """Execute chain with caching."""
            # Check cache first
            logger.info(f"Checking cache for {section_name}...") if self.verbose else None
            logger.info(input_dict.keys()) if self.verbose else None
            if self._cache:
                try:
                    cached_result = self._cache.get(input_dict)

                    if cached_result:
                        logger.info("Using cached result") if self.verbose else None
                        logger.info(cached_result.keys()) if self.verbose else None
                        return cached_result
                    
                    logger.info("No cache hit, invoking chain") if self.verbose else None
                    result = chain_with_fallback.invoke(input_dict)
                    
                    # Cache the result
                    self._cache.set(input_dict, result)
                    return result 
                except Exception as e:
                    logger.error(f"Cache failed: {e}")
            else:
                logger.info("Cache disabled, invoking chain") if self.verbose else None

            # No cache or cache failed, invoke chain
            return chain_with_fallback.invoke(input_dict)
        
        return RunnableLambda(cached_invoke)
        
class SyllabusGeneratorPipeline:
    """Class to compile a hybrid pipeline for generating syllabuses."""
    def __init__(self, model_name="gemini-1.5-pro", model_max_retries=3, verbose=False):
        self.verbose = verbose
        self.model = GoogleGenerativeAI(model=model_name, max_retries=model_max_retries)
        self.cache = LLMCache()  # Initialize the cache  

    def compile(self) -> dict:
        """Compile a hybrid pipeline with sequential and parallel branches."""
        try:
            parsers = ParserFactory.create_parsers()
            chain_builder = ChainBuilder(self.model, parsers, self.cache, self.verbose)

            chains = {}
            chains["course_information"] = chain_builder.build_chain_with_fallback(
                PromptFactory.course_information(
                    parsers["course_information"].get_format_instructions()
                ),
                "CourseInformation",
                "course_information"
            )
            chains["course_description_objectives"] = chain_builder.build_chain_with_fallback(
                PromptFactory.course_description_objectives(
                    parsers["course_description_objectives"].get_format_instructions()
                ),
                "DescriptionObjectives",
                "course_description_objectives"
            )
            chains["course_content"] = chain_builder.build_chain_with_fallback(
                PromptFactory.course_content(
                    parsers["course_content"].get_format_instructions()
                ),
                "CourseContent",
                "course_content"
            )
            chains["policies_procedures"] = chain_builder.build_chain_with_fallback(
                PromptFactory.policies_procedures(
                    parsers["policies_procedures"].get_format_instructions()
                ),
                "PoliciesProcedures",
                "policies_procedures"
            )
            chains["assessment_grading_criteria"] = chain_builder.build_chain_with_fallback(
                PromptFactory.assessment_grading_criteria(
                    parsers["assessment_grading_criteria"].get_format_instructions()
                ),
                "AssessmentGradingCriteria",
                "assessment_grading_criteria"
            )   
            chains["learning_resources"] = chain_builder.build_chain_with_fallback(
                PromptFactory.learning_resources(
                    parsers["learning_resources"].get_format_instructions()
                ),
                "LearningResources",
                "learning_resources"
            )
            chains["course_schedule"] = chain_builder.build_chain_with_fallback(
                PromptFactory.course_schedule(
                    parsers["course_schedule"].get_format_instructions()
                ),
                "CourseSchedule",
                "course_schedule"
            )  

            # Build a parallel pipeline for the chains that can be executed concurrently
            parallel_pipeline = RunnableParallel(
                branches={
                    "assessment_grading_criteria": chains["assessment_grading_criteria"],
                    "learning_resources": chains["learning_resources"],
                    "course_schedule": chains["course_schedule"],
                }
            )

            if self.verbose:
                logger.info("Successfully compiled the hybrid pipeline with context chaining.")

            return {
                "sequential": {
                    "course_information": chains["course_information"],
                    "course_description_objectives": chains["course_description_objectives"],
                    "course_content": chains["course_content"],
                    "policies_procedures": chains["policies_procedures"],
                },
                "parallel": parallel_pipeline
            }    

        except Exception as e:
            logger.error(f"Failed to compile pipeline: {e}")
            raise CompilePipelineError(str(e))
    
def resume_course_content(course_content: List[CourseContentItem]) -> dict:
    """
    Resume the course content with course length and topics for course schedule.
    
    Args:
        course_content: List of CourseContentItem objects
        
    Returns:
        dict: Resumed course content with course length and topics
    """
    course_length = {}
    course_topics = ""
    for content_item in course_content:
        unit_time = content_item["unit_time"]   
        unit_time_value = content_item["unit_time_value"]
        if unit_time in course_length:
            course_length[unit_time] += 1
        else:
            course_length[unit_time] = 1
        course_topics += f"{unit_time_value} {unit_time}: {['topic']}\n"
    
    return {
        "course_length": "".join([f"{v} {k}, " for k, v in course_length.items()])[:-2],
        "course_topics": course_topics
    }
class SyllabusGenerator:
    """
    Main class responsible for generating complete syllabuses using LLM.
    
    Coordinates the pipeline execution, handles errors, and validates the output.
    Uses configurable error thresholds to determine if enough sections were 
    successfully generated.
    """
    def __init__(self , error_threshold:float=0.8, verbose=False):
        self.verbose = verbose
        self.error_threshold = error_threshold

    def generate_syllabus(self, request_args: SyllabusRequestArgs, verbose=True) -> dict:
        """
        Generate a complete syllabus document using the LLM pipeline.
    
        Args:
            request_args: Structured input containing all required syllabus information
            verbose: Whether to log detailed progress information
            
        Returns:
            dict: Complete syllabus with all sections
            
        Raises:
            HTTPException: If syllabus generation fails or validation fails
        """
        try:
            start_time = time.time()

            # Create a new pipeline factory
            pipeline_factory =  SyllabusGeneratorPipeline(verbose=self.verbose)
            # Compile the new hybrid pipeline (sequential + parallel)
            pipeline = pipeline_factory.compile()
        
            # Convert request args to dictionary
            request_dict = request_args.to_dict()

            # Start a trace for the pipeline. This will log all steps and errors in one root trace.
            with ls.trace("Syllabus Pipeline", "chain", project_name="syllabus_generator", inputs=request_dict) as rt:
                # --- Step 1: Generate course_information ---
                logger.info("Generating course information...") if verbose else None
                course_information = pipeline["sequential"]["course_information"].invoke(request_dict)
                # Inject the output into the request for chained prompts
                request_dict["course_information"] = course_information

                request_dict["course_title"] = course_information["course_title"]
                request_dict["grade_level"] = course_information["grade_level"]
                # --- Step 2: Generate course_description_objectives ---
                logger.info("Generating course description and objectives...") if verbose else None
                course_description_objectives = pipeline["sequential"]["course_description_objectives"].invoke(request_dict)
                 
                if "objectives" in course_description_objectives:
                    request_dict["course_objectives"] = course_description_objectives["objectives"] 
                else:
                    # Fallback to the original objectives if the parser fails
                    request_dict["course_objectives"] = request_dict["objectives"]

                # --- Step 3: Generate course_content using the chained course_information ---
                logger.info("Generating course content...") if verbose else None
                course_content = pipeline["sequential"]["course_content"].invoke(request_dict)

                if course_description_objectives.get("status") != "failed":
                    # Resuming course content with course length and topics for course_schedule
                    request_dict["course_resumed_content"] = resume_course_content(course_content)
                else:
                    # Fallback to empty content if the parser fails
                    request_dict["course_resumed_content"] = ""

                # --- Step 4: Generate policies_procedures ---
                logger.info("Generating policies and procedures...") if verbose else None
                policies_procedures = pipeline["sequential"]["policies_procedures"].invoke(request_dict)

                # --- Step 5: Generate parallel outputs for assessment, learning resources, course schedule ---
                logger.info("Generating assessment, learning resources, and course schedule...") if verbose else None
                parallel_outputs = pipeline["parallel"].invoke(request_dict)

                model = SyllabusSchema(
                    course_information=course_information,
                    course_description_objectives=course_description_objectives,
                    course_content=course_content,
                    policies_procedures=policies_procedures,
                    assessment_grading_criteria=parallel_outputs["branches"]["assessment_grading_criteria"],
                    learning_resources=parallel_outputs["branches"]["learning_resources"],
                    course_schedule=parallel_outputs["branches"]["course_schedule"],
                )
                logger.info("Syllabus generated successfully.")

                model = model.dict()
                # Validate the output and calculate error rate
                metadata = self._validate_output(model)
                # End the trace
                rt.end(outputs={"output": model, "metadata": metadata})
                
                end_time = time.time()
                if verbose:
                    logger.info(f"Total generation time: {end_time - start_time:.2f}s")

                return model
            
        except CompilePipelineError as e:
            logger.error(f"Failed to compile pipeline: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate syllabus from LLM")
        except OutputValidationError as e:
            logger.error(f"Failed to validate syllabus: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate syllabus from LLM.")
        except Exception as e:
            logger.error(f"Failed to generate syllabus: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate syllabus from LLM.")
 
    def _validate_output(self, output: dict) -> dict:
        """
        Post-processing validation
        Validate the output and calculate error rate. 
        If the error rate exceeds the threshold, raise an exception.
        """
        error_count = 0
        error_sections = []
        success_sections = []
        for section, result in output.items():
            if isinstance(result, dict) and result.get("error"):
                error_sections.append(section)
                error_count += 1
            else:
                success_sections.append(section)
        
        error_rate = round(error_count / len(output), 2)
        if error_count == len(output):
            raise OutputValidationError("Failed to generate any section.")
        
        if error_rate >= self.error_threshold:
            raise OutputValidationError("Error rate exceeds threshold.")
        
        if error_sections:
            logger.warning(f"Partial failure in sections: {error_sections}.\n Error rate: {error_rate}")

        return {
            "status": error_rate == 0,
            "error_rate": error_rate,
            "error_sections": error_sections,
            "success_sections": success_sections
        }
class InternalError(Exception):
    """Base class for internal errors."""
    pass
class CompilePipelineError(InternalError):
    """Error raised when the pipeline fails to compile."""
    pass
class OutputValidationError(InternalError):
    """Error raised when the output fails validation.    
    
    This occurs when too many sections fail to generate properly
    or when the error rate exceeds the configured threshold.
    """
    pass
