import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Union

from app.tools.notes_generator.core import executor as generate_notes_executor
from app.assistants.utils.assistants_utilities import execute_assistant
from app.services.schemas import GenericAssistantRequest, ToolRequest, ChatRequest, Message, ChatResponse, ToolResponse, NotesGeneratorArgs, NotesResponse
from app.utils.auth import key_check
from app.services.logger import setup_logger
from app.api.error_utilities import InputValidationError, ErrorResponse
from app.tools.utils.tool_utilities import load_tool_metadata, execute_tool, finalize_inputs
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/submit-tool", response_model=Union[ToolResponse, ErrorResponse])
async def submit_tool( data: ToolRequest, _ = Depends(key_check)):
    try:
        # Unpack GenericRequest for tool data
        request_data = data.tool_data

        requested_tool = load_tool_metadata(request_data.tool_id)

        request_inputs_dict = finalize_inputs(request_data.inputs, requested_tool['inputs'])

        result = execute_tool(request_data.tool_id, request_inputs_dict)

        return ToolResponse(data=result)

    except InputValidationError as e:
        logger.error(f"InputValidationError: {e}")

        return JSONResponse(
            status_code=400,
            content=jsonable_encoder(ErrorResponse(status=400, message=e.message))
        )

    except HTTPException as e:
        logger.error(f"HTTPException: {e}")
        return JSONResponse(
            status_code=e.status_code,
            content=jsonable_encoder(ErrorResponse(status=e.status_code, message=e.detail))
        )

@router.post("/assistant-chat", response_model=ChatResponse)
async def assistants( request: GenericAssistantRequest, _ = Depends(key_check) ):

    assistant_group = request.assistant_inputs.assistant_group
    assistant_name = request.assistant_inputs.assistant_name
    user_info = request.assistant_inputs.user_info
    messages = request.assistant_inputs.messages

    result = execute_assistant(assistant_group, assistant_name, user_info, messages)

    formatted_response = Message(
        role="ai",
        type="text",
        payload={"text": result}
    )

    return ChatResponse(data=[formatted_response])

@router.post("/generate-notes", response_model=NotesResponse)
async def generate_notes(
    request: NotesGeneratorArgs,  # Usando o schema existente
    _ = Depends(key_check)
) -> NotesResponse:
    """
    Generates structured notes based on the provided text or file.

    Args:
        request (NotesGeneratorArgs): Object containing input_text, focus, file_url, file_type, and lang.

    Returns:
        NotesResponse: The generated notes in structured format.
    """

    # Extract request data
    input_text = request.input_text
    focus = request.focus
    file_url = request.file_url
    file_type = request.file_type
    lang = request.lang

    # Execute the notes generation logic
    result = generate_notes_executor(input_text, focus, file_url, file_type, lang)

    return NotesResponse(data=result)
