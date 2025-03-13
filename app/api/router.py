import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Union
from app.assistants.utils.assistants_utilities import execute_assistant
from app.services.schemas import GenericAssistantRequest, ToolRequest, ChatRequest, Message, ChatResponse, ToolResponse
from app.utils.auth import key_check
from app.services.logger import setup_logger
from app.api.error_utilities import InputValidationError, ErrorResponse
from app.tools.utils.tool_utilities import load_tool_metadata, execute_tool, finalize_inputs
from app.tools.presentation_generator.tools.slides_generator import SlidesGenerator
import uuid
from fastapi import FastAPI

logger = setup_logger(__name__)
router = APIRouter()
app = FastAPI()

# Initialize presentation contexts in app state if not exists
if not hasattr(app.state, "presentation_contexts"):
    app.state.presentation_contexts = {}

@router.get("/")
def read_root():
    return {"Hello": "World"}

# Handles two-step presentation generation:
# 1. Generate outline with initial inputs
# 2. Generate slides using stored outline and inputs
@router.post("/generate-outline", response_model=Union[ToolResponse, ErrorResponse])
async def generate_outline(data: ToolRequest, _ = Depends(key_check)):
    try:
        # Execute outline generation and store context for slides
        request_data = data.tool_data
        requested_tool = load_tool_metadata(request_data.tool_id)
        request_inputs_dict = finalize_inputs(request_data.inputs, requested_tool['inputs'])
        result = execute_tool(request_data.tool_id, request_inputs_dict)
        
        # Store in app state, to use as context for slides generation
        presentation_id = str(uuid.uuid4())
        app.state.presentation_contexts[presentation_id] = {
            "outline": result,
            "inputs": request_inputs_dict
        }
        
        return ToolResponse(data={
            "outline": result,
            "presentation_id": presentation_id
        })
    
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

@router.post("/generate-slides/{presentation_id}", response_model=Union[ToolResponse, ErrorResponse])
async def generate_slides(presentation_id: str, _ = Depends(key_check)):
    try:
        # Retrieve stored context and generate slides
        context = app.state.presentation_contexts.get(presentation_id)
        if not context:
            raise HTTPException(
                status_code=404, 
                detail="Presentation context not found"
            )
        
        slides = SlidesGenerator(
            outline=context["outline"],
            inputs=context["inputs"]
        ).compile()
        
        return ToolResponse(data=slides)
    
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