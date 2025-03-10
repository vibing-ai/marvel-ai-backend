from pydantic import BaseModel, Field, validator
from typing import List, Dict
from app.services.logger import setup_logger
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel  
from langsmith import trace
from app.services.schemas import SyllabusGeneratorArgsModel
from fastapi import HTTPException
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from functools import lru_cache
from langchain.callbacks import get_openai_callback
import hashlib
import json
import time

logger = setup_logger(__name__)

class SyllabusRequestArgs:
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


class SyllabusGeneratorPipeline:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.model = GoogleGenerativeAI(model="gemini-1.5-pro")
        self.cache = LLMCache()  # Initialize the cache
        self.parsers = {
            "course_information": JsonOutputParser(pydantic_object=CourseInformation),
            "course_description_objectives": JsonOutputParser(pydantic_object=CourseDescriptionObjectives),
            "course_content": JsonOutputParser(pydantic_object=CourseContentItem),
            "policies_procedures": JsonOutputParser(pydantic_object=PoliciesProcedures),
            "assessment_grading_criteria": JsonOutputParser(pydantic_object=AssessmentGradingCriteria),
            "learning_resources": JsonOutputParser(pydantic_object=LearningResource),
            "course_schedule": JsonOutputParser(pydantic_object=CourseScheduleItem),
        }
    def cached_invoke(self, chain, input_dict):
        """Execute chain with caching."""
        # Check cache first
        cached_result = self.cache.get(input_dict)
        if cached_result:
            if self.verbose:
                logger.info("Using cached result")
            return cached_result
        
        # No cache hit, invoke chain
        result = chain.invoke(input_dict)
        
        # Cache the result
        self.cache.set(input_dict, result)
        return result    

    # ===== NEW METHOD: compile_sequential() to build a hybrid pipeline =====
    def compile_hybrid_pipeline(self):
        try:
            # --- Step 1: First sequential chunk - Core course information ---
            # Enhanced prompt for course_information with better guidance for missing fields
            course_info_prompt = ChatPromptTemplate.from_template(
                """
                You are an expert curriculum designer tasked with creating detailed course information.
                
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
                
                Respond in {lang} language.
                
                {format_instructions}
                """
            )
            
            # Create chain for course information
            self.chain_course_information = (
                course_info_prompt
                | self.model 
                | self.parsers["course_information"]
            )
            
            # --- Step 2: First sequential chunk - Course objectives (parallel to course info) ---
            # Enhanced prompt for course objectives
            course_desc_obj_prompt = ChatPromptTemplate.from_template(
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
                
                Respond in {lang} language.
                
                {format_instructions}
                """
            )
            
            # Create chain for course objectives
            self.chain_course_description_objectives = (
                course_desc_obj_prompt
                | self.model 
                | self.parsers["course_description_objectives"]
            )
            
            # --- Step 3: Create separate chains for the remaining steps ---
            # We'll pass the needed values directly in invoke() rather than
            # embedding them in template variables
            
            # Course content prompt
            course_content_prompt = ChatPromptTemplate.from_template(
                """
                You are an expert curriculum designer creating a detailed course content outline.
                
                # Context from Previous Generation Steps
                Course Title: {course_title}
                Grade Level: {grade_level}
                Course Description: {description}
                
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
                
                Respond in {lang} language.
                
                {format_instructions}
                """
            )
            
            # Create chain for course content
            self.chain_course_content = (
                course_content_prompt
                | self.model 
                | self.parsers["course_content"]
            )
            
            # Policies prompt
            policies_prompt = ChatPromptTemplate.from_template(
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
                
                Respond in {lang} language.
                
                {format_instructions}
                """
            )
            
            # Create chain for policies procedures
            self.chain_policies_procedures = (
                policies_prompt
                | self.model 
                | self.parsers["policies_procedures"]
            )
            
            # Assessment prompt
            assessment_prompt = ChatPromptTemplate.from_template(
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
                
                Respond in {lang} language.
                
                {format_instructions}
                """
            )
            
            # Create chain for assessment grading
            self.chain_assessment_grading_criteria = (
                assessment_prompt
                | self.model 
                | self.parsers["assessment_grading_criteria"]
            )
            
            # Learning resources prompt
            learning_resources_prompt = ChatPromptTemplate.from_template(
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
                
                Respond in {lang} language.
                
                {format_instructions}
                """
            )
            
            # Create chain for learning resources
            self.chain_learning_resources = (
                learning_resources_prompt
                | self.model 
                | self.parsers["learning_resources"]
            )
            
            # Course schedule prompt
            course_schedule_prompt = ChatPromptTemplate.from_template(
                """
                You are creating a detailed course schedule based on the course content.
                
                # Course Information
                Course Title: {course_title}
                
                # Course Content Structure
                {course_content}
                
                # Instructions
                1. Create a detailed schedule that follows the course content structure
                2. Match the unit_time format used in the course content (weeks, days, etc.)
                3. Include specific dates or time periods for each topic
                4. Add appropriate activities for each topic that support the learning objectives
                
                Respond in {lang} language.
                
                {format_instructions}
                """
            )
            
            # Create chain for course schedule
            self.chain_course_schedule = (
                course_schedule_prompt
                | self.model 
                | self.parsers["course_schedule"]
            )

            if self.verbose:
                logger.info("Successfully compiled the hybrid pipeline with context chaining.")

        except Exception as e:
            logger.error(f"Failed to compile LLM pipeline: {e}")
            raise HTTPException(status_code=500, detail="Failed to compile LLM pipeline.")
    # ===== END NEW METHOD =====

# ===== Updated generate_syllabus() to use the new hybrid pipeline =====
def generate_syllabus_with_tracing(request_args: SyllabusRequestArgs, verbose=True):
    """
    Wrapper function that creates a single root trace for the entire syllabus generation process.
    """
    # Create a trace for the entire pipeline
    with trace(run_type="chain", name="Complete Syllabus", 
           metadata={"grade_level": request_args.to_dict()["grade_level"],
                     "subject": request_args.to_dict()["subject"]}) as root_trace:
        # Call the actual implementation
        result = generate_syllabus(request_args, verbose=verbose)
        return result
    
def generate_syllabus(request_args: SyllabusRequestArgs, verbose=True):
    try:
        start_time = time.time()
        pipeline = SyllabusGeneratorPipeline(verbose=verbose)
        pipeline.compile_hybrid_pipeline()

        request_dict = request_args.to_dict()
        
        # --- Step 1: Generate course_information and course_description_objectives in parallel ---
        request_dict["format_instructions"] = pipeline.parsers["course_information"].get_format_instructions()
        
        # Use nested tracing for each component
        with trace(run_type="chain", name="CourseInformation"):
            course_information = pipeline.cached_invoke(pipeline.chain_course_information, request_dict)
        
        request_dict["format_instructions"] = pipeline.parsers["course_description_objectives"].get_format_instructions()
        with trace(run_type="chain", name="DescriptionObjectives"):
            course_description_objectives = pipeline.cached_invoke(pipeline.chain_course_description_objectives, request_dict)
        
        # --- Step 2: Create core content that depends on previous outputs ---
        content_input = request_dict.copy()
        content_input["course_title"] = course_information["course_title"]
        content_input["grade_level"] = course_information["grade_level"]
        content_input["description"] = course_information["description"]
        content_input["objectives"] = course_description_objectives["objectives"]
        content_input["format_instructions"] = pipeline.parsers["course_content"].get_format_instructions()
        
        with trace(run_type="chain", name="CourseContent"):
            course_content = pipeline.cached_invoke(pipeline.chain_course_content, content_input)
        
        # --- Step 3: Run policies, assessment, and resources in parallel ---
        # Prepare inputs for parallel processing
        policies_input = request_dict.copy()
        policies_input["course_title"] = course_information["course_title"]
        policies_input["grade_level"] = course_information["grade_level"]
        policies_input["format_instructions"] = pipeline.parsers["policies_procedures"].get_format_instructions()
        
        assessment_input = request_dict.copy()
        assessment_input["course_title"] = course_information["course_title"]
        assessment_input["grade_level"] = course_information["grade_level"]
        assessment_input["objectives"] = course_description_objectives["objectives"]
        assessment_input["format_instructions"] = pipeline.parsers["assessment_grading_criteria"].get_format_instructions()
        
        resources_input = request_dict.copy()
        resources_input["course_title"] = course_information["course_title"]
        resources_input["grade_level"] = course_information["grade_level"]
        resources_input["format_instructions"] = pipeline.parsers["learning_resources"].get_format_instructions()
        
        # Execute parallel tasks using concurrent futures
        from concurrent.futures import ThreadPoolExecutor
        
        # Create a trace for the parallel components
        with trace(run_type="chain", name="ParallelComponents") as parallel_trace:
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all three tasks with their own traces
                def run_policies():
                    with trace(run_type="chain", name="PoliciesProcedures", parent=parallel_trace):
                        return pipeline.chain_policies_procedures.invoke(policies_input)
                
                def run_assessment():
                    with trace(run_type="chain", name="AssessmentGrading", parent=parallel_trace):
                        return pipeline.chain_assessment_grading_criteria.invoke(assessment_input)
                
                def run_resources():
                    with trace(run_type="chain", name="LearningResources", parent=parallel_trace):
                        return pipeline.chain_learning_resources.invoke(resources_input)
                
                # Submit all three tasks to run concurrently
                policies_future = executor.submit(run_policies)
                assessment_future = executor.submit(run_assessment)
                resources_future = executor.submit(run_resources)
                
                # Get results when all complete
                policies_procedures = policies_future.result()
                assessment_grading_criteria = assessment_future.result()
                learning_resources = resources_future.result()
        
        # --- Step 4: Course schedule (depends on course_content) ---
        schedule_input = {
            "course_title": course_information["course_title"],
            "course_content": course_content,
            "lang": request_dict["lang"],
            "format_instructions": pipeline.parsers["course_schedule"].get_format_instructions()
        }
        
        with trace(run_type="chain", name="CourseSchedule"):
            course_schedule = pipeline.chain_course_schedule.invoke(schedule_input)

        # Construct final syllabus
        model = SyllabusSchema(
            course_information=course_information,
            course_description_objectives=course_description_objectives,
            course_content=course_content,
            policies_procedures=policies_procedures,
            assessment_grading_criteria=assessment_grading_criteria,
            learning_resources=learning_resources,
            course_schedule=course_schedule,
        )

        end_time = time.time()
        if verbose:
            logger.info(f"Total generation time: {end_time - start_time:.2f}s")

        return dict(model)

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate syllabus from LLM.")

# ------------------ Existing Schema Definitions (unchanged) ------------------
class CourseInformation(BaseModel):
    course_title: str = Field(description="The course title")
    grade_level: str = Field(description="The grade level")
    description: str = Field(description="The course description")
    @validator('course_title', pre=True)
    def validate_course_title(cls, v):
        if not v or v == "Not specified":
            return "General Course"
        return v
        
    @validator('grade_level', pre=True)
    def validate_grade_level(cls, v):
        if not v or v == "Not specified":
            return "Unspecified Grade Level"
        return v
        
    @validator('description', pre=True)
    def validate_description(cls, v):
        if not v or v == "":
            return "This course provides students with knowledge and skills in the subject area."
        return v

class CourseDescriptionObjectives(BaseModel):
    objectives: List[str] = Field(description="The course objectives")
    intended_learning_outcomes: List[str] = Field(description="The intended learning outcomes of the course")

class CourseContentItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course content")
    unit_time_value: int = Field(description="The unit of time value for the course content")
    topic: str = Field(description="The topic per unit of time for the course content")

class PoliciesProcedures(BaseModel):
    attendance_policy: str = Field(description="The attendance policy of the class")
    late_submission_policy: str = Field(description="The late submission policy of the class")
    academic_honesty: str = Field(description="The academic honesty policy of the class")

class AssessmentMethod(BaseModel):
    type_assessment: str = Field(description="The type of assessment")
    weight: int = Field(description="The weight of the assessment in the final grade")

class AssessmentGradingCriteria(BaseModel):
    assessment_methods: List[AssessmentMethod] = Field(description="The assessment methods")
    grading_scale: dict = Field(description="The grading scale")

class LearningResource(BaseModel):
    title: str = Field(description="The book title of the learning resource")
    author: str = Field(description="The book author of the learning resource")
    year: int = Field(description="The year of creation of the book")

class CourseScheduleItem(BaseModel):
    unit_time: str = Field(description="The unit of time for the course schedule item")
    unit_time_value: int = Field(description="The unit of time value for the course schedule item")
    date: str = Field(description="The date for the course schedule item")
    topic: str = Field(description="The topic for the learning resource")
    activity_desc: str = Field(description="The descrition of the activity for the learning resource")

class SyllabusSchema(BaseModel):
    course_information: CourseInformation = Field(description="The course information")
    course_description_objectives: CourseDescriptionObjectives = Field(description="The objectives of the course")
    course_content: List[CourseContentItem] = Field(description="The content of the course")
    policies_procedures: PoliciesProcedures = Field(description="The policies procedures of the course")
    assessment_grading_criteria: AssessmentGradingCriteria = Field(description="The asssessment grading criteria of the course")
    learning_resources: List[LearningResource] = Field(description="The learning resources of the course")
    course_schedule: List[CourseScheduleItem] = Field(description="The course schedule")

