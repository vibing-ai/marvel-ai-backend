from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.router import router
from app.services.logger import setup_logger
from app.api.error_utilities import ErrorResponse
import os

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Application Startup")

    # Check required environment variables
    required_vars = ['GOOGLE_API_KEY', 'PROJECT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

    logger.info("Successfully completed application startup")
    yield
    logger.info("Application shutdown")

app = FastAPI(
    lifespan=lifespan,
    root_path="",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        message = error['msg']
        error_detail = f"Error in field '{field}': {message}"
        errors.append(error_detail)
        logger.error(error_detail)

    error_response = ErrorResponse(status=422, message=errors)
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )

app.include_router(router)