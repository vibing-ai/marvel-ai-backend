# Import necessary modules and dependencies
from app.services.logger import setup_logger  # Logger setup for debugging and error tracking
from app.tools.syllabus_generator.tools import SyllabusRequestArgs, generate_syllabus  # Import syllabus generator utilities
from app.utils.document_loaders_summarization import (
    generate_summary_from_img,  # Function to generate summary from images
    summarize_transcript_youtube_url,  # Function to summarize YouTube transcript
    get_summary  # Function to extract summary from other file types
)
from app.api.error_utilities import SyllabusGeneratorError  # Custom error handling class for syllabus generation
from app.services.schemas import SyllabusGeneratorArgsModel  # Schema model for syllabus generation arguments
from langchain.chains import LLMChain  # LangChain module for chaining LLM calls
from langchain.prompts import PromptTemplate  # LangChain module for prompt templates

# Initialize logger
logger = setup_logger()

def executor(
    grade_level: str,
    subject: str,
    course_description: str,
    objectives: str,
    required_materials: str,
    grading_policy: str,
    policies_expectations: str,
    course_outline: str,
    additional_notes: str,
    file_url: str,
    file_type: str,
    lang: str,
    verbose: bool = True
):
    if verbose:
        logger.info(f"File URL loaded: {file_url}")  # Log the file URL being processed

    try:
        # Step 1: Process the input file and generate a summary
        if file_type == 'img':
            summary = generate_summary_from_img(file_url)  # Extract summary from an image
        elif file_type == 'youtube_url':
            summary = summarize_transcript_youtube_url(file_url, verbose=verbose)  # Summarize YouTube transcript
        else:
            summary = get_summary(file_url, file_type, verbose=verbose)  # Extract summary from other file types

        # Step 2: Create an instance of SyllabusGeneratorArgsModel with user inputs
        syllabus_args_model = SyllabusGeneratorArgsModel(
            grade_level=grade_level,
            subject=subject,
            course_description=course_description,
            objectives=objectives,
            required_materials=required_materials,
            grading_policy=grading_policy,
            policies_expectations=policies_expectations,
            course_outline=course_outline,
            additional_notes=additional_notes,
            file_url=file_url,
            file_type=file_type,
            lang=lang
        )

        # Step 3: Create a request object containing the syllabus arguments and summary
        request_args = SyllabusRequestArgs(syllabus_args_model, summary)

        # Sequential-Parallel Hybrid Implementation

        # Step 4: Generate core course information first (sequential step)
        course_info_chain = LLMChain(
            llm=generate_syllabus,
            prompt=PromptTemplate(
                input_variables=["grade_level", "subject", "course_description"],
                template="Generate the basic course information including name, subject, and description for a {grade_level} {subject} course. Description: {course_description}"
            )
        )
        course_info = course_info_chain.run(request_args)  # Generate core course information

        # Step 5: Prepare context-enriched request arguments by including generated course information
        context_enriched_request_args = {**request_args, **course_info}

        # Step 6: Run parallel AI calls using LangChain for learning objectives, course content, and policies
        learning_objectives_chain = LLMChain(
            llm=generate_syllabus,
            prompt=PromptTemplate(
                input_variables=["objectives", "course_info"],
                template="Using the provided course information: {course_info}, generate learning objectives: {objectives}"
            )
        )

        course_content_chain = LLMChain(
            llm=generate_syllabus,
            prompt=PromptTemplate(
                input_variables=["course_outline", "course_info"],
                template="Using the provided course information: {course_info}, generate a detailed course outline: {course_outline}"
            )
        )

        policies_chain = LLMChain(
            llm=generate_syllabus,
            prompt=PromptTemplate(
                input_variables=["policies_expectations", "course_info"],
                template="Using the provided course information: {course_info}, generate policies and expectations: {policies_expectations}"
            )
        )

        # Execute parallel tasks for the remaining sections
        learning_objectives = learning_objectives_chain.run(context_enriched_request_args)
        course_content = course_content_chain.run(context_enriched_request_args)
        policies = policies_chain.run(context_enriched_request_args)

        # Step 7: Aggregate all generated components into the final syllabus
        final_syllabus = {
            "course_info": course_info,
            "learning_objectives": learning_objectives,
            "course_content": course_content,
            "policies": policies
        }

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {str(e)}")  # Log the error
        raise SyllabusGeneratorError(f"Failed to generate syllabus: {str(e)}") from e  # Raise a custom error

    return final_syllabus













