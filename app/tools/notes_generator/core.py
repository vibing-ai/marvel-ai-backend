from app.tools.notes_generator.tools import NoteGeneratorPipeline
from app.services.schemas import NoteGeneratorArgs
from app.utils.document_loaders import get_docs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from langchain_core.documents import Document
logger = setup_logger()

def executor(
    focus: str,
    page_layout: str,
    text_input: str,
    file_type: str,
    file_url: str,
    lang: str,
    verbose=True
):
    """
    Executor function for the Notes Generator tool.
    
    Args:
        focus (str): The focus or topic of the notes.
        page_layout (str): The structure or template for the notes (e.g., bullet points, paragraphs, tables).
        text_input (str): Direct text input for note generation.
        file_type (str): Type of the uploaded file (e.g., CSV, PDF, DOCX, PPT, Plain Text).
        file_url (str): URL of the uploaded file.
        lang (str): Language of the input.
        verbose (bool): Flag for verbose logging.
    
    Returns:
        dict: Generated notes in the specified format.
    
    Raises:
        ToolExecutorError: If there is an error during execution.
        ValueError: If an unexpected error occurs.
    """
    try:
        # Check if page layout is provided
        if not page_layout:
            raise ValueError("No page layout provided for note generation.")
        
        # Check if any input is provided for note generation
        if not any([text_input, file_url,focus,file_type]):
            raise ValueError("No input provided for note generation.")        
            
        # Check if url is provided without file type
        if file_url and not file_type: 
            raise ValueError("No file type provided for document loading.") 
        
         # Log file type if provided
        if file_type:
            logger.info(f"Generating docs from {file_type} file.")

        # Load documents if a file URL is provided
        docs = None
        
           
        if file_url and file_type:
            logger.info(f"Loading documents from {file_url}.")
            docs = get_docs(file_url, file_type, True)
        

        # If user provides text, add it as a Document
        if text_input:
            logger.info("Using provided text input for note generation.")
            text_doc = Document(page_content=text_input)
            if docs:  
                docs.append(text_doc)  # Append to existing list
            else:
                docs = [text_doc]  # Create a new list with the text
            
            print("length of docs;",len(docs))

        # Initialize the NoteGeneratorArgs schema
        note_generator_args = NoteGeneratorArgs(
            focus=focus,
            page_layout=page_layout,
            text_input=text_input,
            file_type=file_type,
            file_url=file_url,
            lang=lang
        )
    
        # Initialize the NoteGeneratorPipeline
        note_generator = NoteGeneratorPipeline(args=note_generator_args, verbose=verbose)

        # Generate notes
        output = note_generator.generate_notes(docs)

        logger.info("Notes generated successfully.")
        return output

    except LoaderError as e:
        error_message = f"Error loading documents: {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)