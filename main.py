"""
JanMitra AI Phase 1 Backend - Main Application Entry Point

A FastAPI-based government scheme eligibility evaluation system with
deterministic rule-based evaluation and DynamoDB storage.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from datetime import datetime
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from utils.logging_config import configure_structured_logging
from utils.masking import mask_aadhaar, mask_phone, mask_income

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import HTTPBearer
from middleware.auth import verify_token, create_access_token

# Load environment variables
load_dotenv()

# Configure structured JSON logging
configure_structured_logging(log_level="INFO")

logger = logging.getLogger(__name__)

# Configure Rate Limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for FastAPI application"""
    logger.info(
        "JanMitra AI Phase 1 Backend starting up",
        extra={
            "event": "application_startup",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )
    
    print("\n" + "#"*60)
    print("!!! JANMITRA AI BACKEND: READY & LOGGING ALL REQUESTS !!!")
    print("#"*60 + "\n")
    import sys
    sys.stdout.flush()
    yield
    
    logger.info(
        "JanMitra AI Phase 1 Backend shutting down",
        extra={
            "event": "application_shutdown",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

from models.config import Settings
settings = Settings()

# Create FastAPI application
app = FastAPI(
    title="JanMitra AI Phase 1 Backend Secure",
    description="Government scheme eligibility evaluation system with Zero-Trust Security",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if settings.app_env.lower() == "production" else "/docs",
    redoc_url=None if settings.app_env.lower() == "production" else "/redoc",
    openapi_url=None if settings.app_env.lower() == "production" else "/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Request Logger
@app.middleware("http")
async def debug_request_logger(request: Request, call_next):
    """Logs the path of every incoming request to help debug connectivity."""
    print(f"\n>>> INCOMING REQUEST: {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    import sys
    sys.stdout.flush()
    logger.info(f"DEBUG: Request to {request.method} {request.url.path}")
    return await call_next(request)

# Middleware to handle malformed JSON
@app.middleware("http")
async def catch_json_errors(request: Request, call_next):
    """
    Middleware to catch and handle malformed JSON in request bodies.
    
    This catches JSON parsing errors that occur before Pydantic validation
    and returns a user-friendly 400 error response.
    
    Requirements: 2.4
    """
    try:
        return await call_next(request)
    except json.JSONDecodeError as e:
        logger.warning(
            "Malformed JSON in request",
            extra={
                "event": "json_parse_error",
                "path": request.url.path,
                "error": str(e),
                "client_host": request.client.host if request.client else None
            }
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "json_parse_error",
                "message": "Request body contains malformed JSON",
                "details": [{
                    "field": "body",
                    "error": f"JSON parsing failed: {str(e)}"
                }]
            }
        )
    except Exception:
        # Let other exceptions propagate normally
        return await call_next(request)

# Custom exception handler for validation errors
# Requirement 2.4: Return HTTP 400 with error description for invalid UserProfile
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for Pydantic validation errors.
    
    Converts FastAPI's default 422 Unprocessable Entity responses to 400 Bad Request
    with user-friendly error messages for malformed UserProfile data.
    
    Handles:
    - Missing required fields
    - Invalid data types (non-numeric age, income, land_size)
    - Malformed JSON in request body
    - Empty or whitespace-only string fields
    - Out-of-range values (age, income, land_size)
    
    Requirements: 2.4
    """
    errors = exc.errors()
    
    # Format error messages for better readability
    error_details = []
    for error in errors:
        field_path = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        error_type = error["type"]
        error_msg = error["msg"]
        
        # Create user-friendly error messages
        if error_type == "missing":
            detail = f"Field '{field_path}' is required but missing"
        elif error_type in ["int_parsing", "float_parsing"]:
            detail = f"Field '{field_path}' must be a valid number"
        elif error_type == "string_too_short":
            detail = f"Field '{field_path}' cannot be empty"
        elif error_type in ["less_than", "greater_than", "less_than_equal", "greater_than_equal"]:
            detail = f"Field '{field_path}' value is out of valid range: {error_msg}"
        elif error_type == "json_invalid":
            detail = "Request body contains malformed JSON"
        else:
            detail = f"Field '{field_path}': {error_msg}"
        
        error_details.append({
            "field": field_path,
            "error": detail
        })
    
    logger.warning(
        "Validation error in request",
        extra={
            "event": "validation_error",
            "path": request.url.path,
            "error_count": len(error_details),
            "errors": error_details,
            "client_host": request.client.host if request.client else None
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "validation_error",
            "message": "Invalid UserProfile data provided",
            "details": error_details
        }
    )


@app.get("/auth/anonymous-token")
@app.get("/api/auth/anonymous-token")
@limiter.limit("10/minute")
async def get_anonymous_token(request: Request):
    """Generates an anonymous JWT token for frontend access to pass the HTTPBearer Zero-Trust layer"""
    from middleware.auth import create_access_token
    from datetime import timedelta
    access_token = create_access_token(data={"sub": "anonymous_user"}, expires_delta=timedelta(hours=24))
    return {"access_token": access_token, "token_type": "bearer"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "service": "JanMitra AI Phase 1 Backend",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/api/health",
            "system_health": "/api/system-health",
            "evaluate": "/api/evaluate",
            "schemes": "/api/schemes",
            "chat": "/api/chat",
            "voice_query": "/api/voice/query",
            "upload_audio": "/api/upload-audio",
            "upload_document": "/api/upload-document",
            "anonymous_token": "/api/auth/anonymous-token",
        }
    }

# Register routes – all under /api prefix for frontend compatibility
from routes import health, evaluation, schemes, voice, chat, document, chat_routes, system_health
from routes import auth, feedback, application, content_routes

app.include_router(system_health.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")
app.include_router(schemes.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(chat_routes.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(application.router, prefix="/api")
app.include_router(content_routes.router, prefix="/api")

# Legacy routes (no prefix) for backward compatibility
app.include_router(health.router)
app.include_router(evaluation.router)
app.include_router(voice.router)
app.include_router(document.router)
app.include_router(auth.router)  # Add auth here too for proxy compatibility

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
