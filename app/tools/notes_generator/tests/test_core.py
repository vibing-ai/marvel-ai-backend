import pytest
from app.tools.notes_generator.core import executor
from app.tools.notes_generator.tools import GenerateNotesOutput
from app.tools.notes_generator.tools import NoteGeneratorPipeline
from app.tools.notes_generator.tools import Document
from app.tools.notes_generator.core import NoteGeneratorArgs
from langchain_core.output_parsers import JsonOutputParser
from app.tools.notes_generator.tools import BulletPoints

 
base_attributes = {
    "focus": "Summarize the key steps of photosynthesis.",
    "page_layout": "bullet points",
    "text_input": "Photosynthesis is a process used by plants to convert sunlight into energy.",
    "file_type": "pdf",
    "file_url": "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd",
    "lang": "en"
    
}
mock_args = NoteGeneratorArgs(
        focus = base_attributes["focus"],
        page_layout = base_attributes["page_layout"],
        text_input = base_attributes["text_input"],
        file_type = base_attributes["file_type"],
        file_url = base_attributes["file_url"],
        lang = base_attributes["lang"]
    )
mock_parser = JsonOutputParser(pydantic_object=BulletPoints)


#Test the executor function (Integration test)
def test_executor_normal_operation():
    """Test the executor function with valid inputs."""
    result = executor(
        focus=base_attributes["focus"],
        page_layout=base_attributes["page_layout"],
        text_input=base_attributes["text_input"],
        file_type=base_attributes["file_type"],
        file_url=base_attributes["file_url"],
        lang=base_attributes["lang"],
        verbose=False        
    )
    
    assert isinstance(result, BulletPoints)
    assert hasattr(result, "title")
    assert hasattr(result, "notes")


 
# def test_executor_no_page_layout():
#     """Test the executor function with no page layout provided."""
#     with pytest.raises(ValueError, match="No page layout provided for note generation."):
#         executor(
#             focus=base_attributes["focus"],
#             page_layout="",
#             text_input=base_attributes["text_input"],
#             file_type=base_attributes["file_type"],
#             file_url=base_attributes["file_url"],
#             lang=base_attributes["lang"],
#             verbose=False            
#         )

def test_executor_no_input():
    """Test the executor function with no input provided."""
    with pytest.raises(ValueError, match="No input provided for note generation."):
        executor(
            focus="",
            page_layout=base_attributes["page_layout"],
            text_input="",
            file_type="",
            file_url="",
            lang=base_attributes["lang"],
            verbose=False
        )
def test_executor_no_filetype__error():
    """Test the executor function without a file type."""

    with pytest.raises(ValueError, match="Error in executor: No file type provided for document loading."):
        executor(
            focus=base_attributes["focus"],
            page_layout=base_attributes["page_layout"],
            text_input="",
            file_type="",
            file_url=base_attributes["file_url"],
            lang=base_attributes["lang"],
            verbose=False
        )
    
def test_executor_loader_error():
    """Test the executor function without an invalid filetype and fileurl."""

    with pytest.raises(ValueError, match="Error in executor: Document loading failed"):
        executor(
            focus=base_attributes["focus"],
            page_layout=base_attributes["page_layout"],
            text_input="",
            file_type="Invalid",
            file_url="Invalid_url",
            lang=base_attributes["lang"],
            verbose=False
        )
#Test for NoteGeneratorPipeline
def test_note_generator_pipeline_init():
    """Test initialization of NoteGeneratorPipeline."""
    pipeline = NoteGeneratorPipeline(args=None, verbose=False)
    assert pipeline.args is None
    assert pipeline.verbose is False

def test_note_generator_pipeline_compile_vectorstore():
    """Test the compile_vectorstore method."""
    pipeline = NoteGeneratorPipeline(args=None, verbose=False)
    documents = [Document(page_content="Sample document content")]
    pipeline.compile_vectorstore(documents)
    assert pipeline.vectorstore is not None
    assert pipeline.retriever is not None

# def test_note_generator_pipeline_generate_context():
#     """Test the generate_context method."""
#     pipeline = NoteGeneratorPipeline(args=None, verbose=False)
#     documents = [Document(page_content="Photosynthesis is a process used by plants to convert sunlight into energy.")]
#     pipeline.compile_vectorstore(documents)
#     context = pipeline.generate_context("Provide general context for the topic to create notes.")
#     assert isinstance(context, list)

# def test_note_generator_pipeline_compile_pipeline():
    # """Test the compile_pipeline method."""   
    # pipeline = NoteGeneratorPipeline(args=None, verbose=False)
    # pipeline.args = mock_args
    # pipeline.parsers = JsonOutputParser(pydantic_object=BulletPoints)
    # compiled_pipeline = pipeline.compile_pipeline()
    # assert compiled_pipeline is not None

# def test_note_generator_pipeline_generate_notes():
#     """Test the generate_notes method."""
#     pipeline = NoteGeneratorPipeline(args=None, verbose=False)
#     pipeline.args = mock_args
#     pipeline.parsers = mock_parser
#     documents = [Document(page_content=base_attributes["text_input"])]
#     result = pipeline.generate_notes(documents)
#     assert isinstance(result, GenerateNotesOutput)
#     assert result.title == "Generated Notes in bullet points format"
#     assert isinstance(result.notes, str)

def test_note_generator_pipeline_invalid_page_layout():
    """Test the generate_notes method with an invalid page layout."""
    pipeline = NoteGeneratorPipeline(args=None, verbose=False)
    pipeline.args=mock_args
    pipeline.args.page_layout = "invalid"
    pipeline.parsers = mock_parser
    with pytest.raises(ValueError) as exc_info:
        pipeline.generate_notes([])
        assert isinstance(exc_info.value, ValueError)

# def test_generate_notes_output_model():
#     """Test the GenerateNotesOutput model."""
#     output = GenerateNotesOutput(title="Test Title", notes="Test Notes")
#     assert output.title == "Test Title"
#     assert output.notes == "Test Notes"




    