import re
import json
import hashlib
import time
from typing import List, Dict
from functools import lru_cache
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnableLambda  
from langchain_core.tracers.schemas import Run
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
                {course_objectives}
                
                # Additional Context
                Course Outline: {course_outline}
                Summary: {summary}

                # Design Instructions
                1. Create a logical sequence of content units that align with the learning objectives and course description
                2. For each unit, provide:
                    - A clear, descriptive title
                    - A brief description of the unit's focus
                    - 3-5 key topics or concepts covered
                    - How this unit connects to the learning objectives
                3. Ensure content builds progressively, with later units building on earlier foundations
                4. Include depth and breadth appropriate for the specified grade level
                5. If no course outline is provided, develop one based on standard curriculum patterns for this subject
                6. Focus on content organization rather than scheduling aspects
                7. Each unit should represent a coherent body of knowledge rather than a time period
                8. Include any specialized vocabulary or frameworks students will need to master
                9. Respond in {lang} language.

                # Output Guidance
                ## Answer with a valid JSON object, returning a list of CourseContentItem objects.
                class CourseContentItem(BaseModel):
                    unit_sequence: int = Field(description="The sequential unit/module number in the course")
                    title: str = Field(description="The title of the unit")
                    description: str = Field(description="A brief summary of the unit's content"")
                    key_topics: List[str] = Field(description="The key topics for the unit")
                    learning_outcomes: List[str] = Field(description="The learning outcomes for the unit")
                """
            ),
            input_variables=["course_information", "course_outline", "lang", "summary", "course_objectives"],
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
                Learning Objectives: {course_objectives}
                
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
            input_variables=["grading_policy", "lang", "course_title", "grade_level", "course_objectives"],
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
                Course Content: {course_content}
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
            input_variables=["required_materials", "lang", "course_title", "subject", "grade_level", "course_content"],
            partial_variables={"format_instructions": parser_intructions},
        )
    
    @staticmethod
    def course_schedule(parser_intructions: str) -> PromptTemplate:
        """Generate a prompt for constructing a detailed course schedule."""
        return PromptTemplate(
            template=(
                """
                You are an expert educational planner creating a comprehensive course schedule based on established course content.
                
                # Course Information
                Course Title: {course_title}
                Grade Level: {grade_level}
                Course outline informed by the user: {course_outline}
                # Course Content Structure
                {course_content}
                
                # Instructions
                1. Create a detailed schedule that transforms the course content into a chronological delivery plan
                2. For each session, provide:
                    - Session number and date
                    - Topic from the course content being covered
                    - Specific learning activities planned for the session
                3. Ensure appropriate pacing across the entire course timeline
                4. Include variety in learning activities (lectures, discussions, group work, etc.)
                5. Allocate sufficient time for complex topics and review sessions
                6. Schedule assessments at logical points in the learning progression
                7. Account for any holidays or breaks in the academic calendar
                8. Respond in {lang} language.

                # OUTPUT GUIDANCE
                    - Create a realistic schedule that allows sufficient time for each topic
                    - Balance content coverage with appropriate depth of engagement
                    - Account for scaffolding and skill development over time
                    - Ensure assessment timing aligns with learning progression
                    - Consider student workload and cognitive load in your planning

                # Answer with a valid JSON object, returning a list of CourseScheduleItem objects.
                class CourseScheduleItem(BaseModel):
                    session_number: int = Field(description="The sequential session number in the course schedule")
                    date: str = Field(description="The scheduled date for this session (format: YYYY-MM-DD)")
                    time_frame: str = Field(description="The duration of the session (e.g., '2 days', '1 week', '1 month')")
                    topic: str = Field(description="The main topic covered in this session")
                    activity_desc: str = Field(description="A brief description of the planned learning activity for this session")
                """
            ),
            input_variables=["course_outline", "lang", "course_title", "grade_level", "course_content"]
        )
class LLMCache:
    """LRU cache for LLM responses to reduce redundant calls."""
    
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []  # Track access order for LRU implementation
    
    def _get_key(self, input_dict):
        """Create a deterministic hash from the input dictionary."""
        # Sort the dictionary to ensure consistent hashing
        serialized = json.dumps(input_dict, sort_keys=True)
        return hashlib.md5(serialized.encode()).hexdigest()
    
    def get(self, input_dict):
        """Retrieve cached result if available."""
        key = self._get_key(input_dict)
        if key in self.cache:
            # Update access order (move to end = most recently used)
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache.get(key)
        return None
    
    def set(self, input_dict, result):
        """Cache the result using LRU eviction policy."""
        key = self._get_key(input_dict)
        
        # If cache is full, remove least recently used item
        if len(self.cache) >= self.max_size and key not in self.cache:
            if self.access_order:  # Make sure we have items to remove
                lru_key = self.access_order.pop(0)  # Remove first (least recently used)
                if lru_key in self.cache:
                    del self.cache[lru_key]
        
        # Add new item to cache and update access order
        self.cache[key] = result
        
        # Update access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)  # Add to end (most recently used)

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
    
    @staticmethod
    def fn_start(run_obj: Run):
        logger.info(f"Generating section: {run_obj.name}, start_time: {run_obj.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    @staticmethod
    def fn_end(run_obj: Run):
        logger.info(f"Completed section: {run_obj.name}, end_time: {run_obj.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

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
        return chain_with_fallback.with_config(run_name=section_name).with_listeners(on_start=self.fn_start, on_end=self.fn_end)

    # TODO: Add caching to the chain
    # def build_chain_with_cache_fallback(       
    #         self, 
    #         prompt: PromptTemplate, 
    #         section_name: str, 
    #         parser_key: str) -> Runnable:
    #     """Build a chain with a prompt, model, parser, and caching and fallback."""

    #     chain_with_fallback = self.build_chain_with_fallback(prompt, section_name, parser_key)

    #     def cached_invoke(input_dict):
    #         """Execute chain with caching."""
    #         # Check cache first
    #         logger.info(f"Checking cache for {section_name}...") if self.verbose else None
    #         logger.info(input_dict.keys()) if self.verbose else None
    #         if self._cache:
    #             try:
    #                 cached_result = self._cache.get(input_dict)

    #                 if cached_result:
    #                     logger.info("Using cached result") if self.verbose else None
    #                     logger.info(cached_result.keys()) if self.verbose else None
    #                     return cached_result
                    
    #                 logger.info("No cache hit, invoking chain") if self.verbose else None
    #                 result = chain_with_fallback.invoke(input_dict)
                    
    #                 # Cache the result
    #                 self._cache.set(input_dict, result)
    #                 return result 
    #             except Exception as e:
    #                 logger.error(f"Cache failed: {e}")
    #         else:
    #             logger.info("Cache disabled, invoking chain") if self.verbose else None

    #         # No cache or cache failed, invoke chain
    #         return chain_with_fallback.invoke(input_dict)
        
    #     return RunnableLambda(cached_invoke)
        
class PipelineStep:
    """Represents a single step in the pipeline with its dependencies and execution mode."""
    def __init__(self, name: str, prompt_factory, parser_key: str, dependencies: List[str] = None, 
                 execution_mode: str = "sequential"):
        self.name = name
        self.prompt_factory = prompt_factory
        self.parser_key = parser_key
        self.dependencies = dependencies or []
        self.execution_mode = execution_mode  # "sequential" or "parallel"
        self.chain = None

class SyllabusGeneratorPipeline:
    """Class to compile a hybrid pipeline for generating syllabuses."""
    def __init__(self, model_name="gemini-1.5-pro", model_max_retries=3, verbose=False):
        self.verbose = verbose
        self.model = GoogleGenerativeAI(model=model_name, max_retries=model_max_retries)
        self.cache = None
        # self.cache = LLMCache() 
        # Cache implementation is on hold for now as it is needed a more robust caching mechanism
        
        # Define pipeline steps with their dependencies
        self.steps = {
            "course_information": PipelineStep(
                name="course_information",
                prompt_factory=PromptFactory.course_information,
                parser_key="course_information"
            ),
            "course_description_objectives": PipelineStep(
                name="course_description_objectives",
                prompt_factory=PromptFactory.course_description_objectives,
                parser_key="course_description_objectives",
                dependencies=["course_information"]
            ),
            "course_content": PipelineStep(
                name="course_content",
                prompt_factory=PromptFactory.course_content,
                parser_key="course_content",
                dependencies=["course_information", "course_description_objectives"]
            ),
            "policies_procedures": PipelineStep(
                name="policies_procedures",
                prompt_factory=PromptFactory.policies_procedures,
                parser_key="policies_procedures",
                dependencies=["course_information"]
            ),
            "assessment_grading_criteria": PipelineStep(
                name="assessment_grading_criteria",
                prompt_factory=PromptFactory.assessment_grading_criteria,
                parser_key="assessment_grading_criteria",
                dependencies=["course_information", "course_description_objectives"],
                execution_mode="parallel"
            ),
            "learning_resources": PipelineStep(
                name="learning_resources",
                prompt_factory=PromptFactory.learning_resources,
                parser_key="learning_resources",
                dependencies=["course_information"],
                execution_mode="parallel"
            ),
            "course_schedule": PipelineStep(
                name="course_schedule",
                prompt_factory=PromptFactory.course_schedule,
                parser_key="course_schedule",
                dependencies=["course_content"],
                execution_mode="parallel"
            )
        }

    def _build_chain(self, chain_builder, step: PipelineStep) -> Runnable:
        """Build a chain for a given step."""
        return chain_builder.build_chain_with_fallback(
            step.prompt_factory(chain_builder.parsers[step.parser_key].get_format_instructions()),
            step.name.capitalize(),
            step.parser_key
        )

    def compile(self) -> List[Runnable]:
        """Compile the pipeline and return a list of runnables in execution order."""

        try:
            parsers = ParserFactory.create_parsers()
            chain_builder = ChainBuilder(self.model, parsers, self.cache, self.verbose)
            
            # Build all chains
            for step in self.steps.values():
                step.chain = self._build_chain(chain_builder, step)
            
            if self.verbose:
                logger.info("Successfully compiled the pipeline.")
            
            first_runnable = RunnableParallel({
                "course_information": self.steps["course_information"].chain,
                "course_description_objectives": self.steps["course_description_objectives"].chain
            })

            second_runnable = RunnableParallel({
                "course_content": self.steps["course_content"].chain,
                "assessment_grading_criteria": self.steps["assessment_grading_criteria"].chain,
                "policies_procedures": self.steps["policies_procedures"].chain,
            })
            
            third_runnable = RunnableParallel({
                "course_schedule": self.steps["course_schedule"].chain,
                "learning_resources": self.steps["learning_resources"].chain,
            })
            return [first_runnable, second_runnable, third_runnable]
            
        except Exception as e:
            logger.error(f"Failed to compile pipeline: {e}")
            raise CompilePipelineError(str(e))

class SyllabusGenerator:
    """
    Main class responsible for generating complete syllabuses using LLM.
    
    Coordinates the pipeline execution, handles errors, and validates the output.
    Uses configurable error thresholds to determine if enough sections were 
    successfully generated.
    """

    def __init__(self, error_threshold:float=0.8, verbose=False):

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
            pipeline_factory = SyllabusGeneratorPipeline(verbose=self.verbose)
            # Compile the pipeline to get list of runnables
            runnables = pipeline_factory.compile()
        
            # Convert request args to dictionary
            request_dict = request_args.to_dict()

            # Start a trace for the pipeline
            with ls.trace("Syllabus Pipeline", "chain", project_name="syllabus_generator", inputs=request_dict) as rt:
                # Execute each runnable in sequence
                results = {}
                for i, runnable in enumerate(runnables):
                    query_dict = {
                        **request_dict,
                        **results
                    }
                    if isinstance(runnable, RunnableParallel):
                        parallel_results = runnable.invoke(query_dict)
                        for step_name, value in parallel_results.items():
                            results[step_name] = value
                            
                            # Special handling for course_information
                            if step_name == "course_information":
                                request_dict["course_title"] = value.get("course_title")
                                request_dict["grade_level"] = value.get("grade_level")
                            
                            # Special handling for course_description_objectives
                            if step_name == "course_description_objectives":
                                if "objectives" in value:
                                    request_dict["course_objectives"] = value["objectives"]
                                else:
                                    request_dict["course_objectives"] = request_dict.get("objectives", "")
                    else:
                        # Handle sequential execution
                        step_name = runnable.config.get("run_name", "").lower()
                        result = runnable.invoke(query_dict)
                        # Update request_dict and results with the step name as key
                        if isinstance(result, dict) or isinstance(result, list):
                            results[step_name] = result 
         

                # Create the final syllabus model
                model = SyllabusSchema(
                    course_information=results.get("course_information"),
                    course_description_objectives=results.get("course_description_objectives"),
                    course_content=results.get("course_content"),
                    policies_procedures=results.get("policies_procedures"),
                    assessment_grading_criteria=results.get("assessment_grading_criteria"),
                    learning_resources=results.get("learning_resources"),
                    course_schedule=results.get("course_schedule"),
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
            "status": "success" if error_rate == 0 else "partial_success",
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