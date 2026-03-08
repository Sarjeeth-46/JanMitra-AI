"""
Chat Routes for JanMitra AI intelligent assistant.

Defines the POST /chat endpoint that leverages Amazon Bedrock.
"""

from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import uuid

from services.bedrock_service import BedrockService
from models.user_profile import UserProfile
from models.evaluation_result import EvaluationResult

router = APIRouter(prefix="/v2", tags=["chat-v2"])
logger = logging.getLogger(__name__)

# Initialize Bedrock Service
# Note: In a production environment, you might use dependency injection
bedrock_service = BedrockService()

class ChatRequest(BaseModel):
    """Request schema for the Bedrock-powered chat."""
    user_message: str = Field(..., description="The message from the user")
    user_profile: UserProfile = Field(..., description="Current profile of the user")
    eligibility_results: List[EvaluationResult] = Field(..., description="Results from the rule engine")
    session_id: Optional[str] = Field(None, description="Unique session ID for memory")

class ChatResponse(BaseModel):
    """Response schema for the Bedrock-powered chat."""
    response_text: str
    missing_fields: List[str]
    recommended_next_step: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Intelligent chat endpoint using Amazon Bedrock.
    
    Provides explanations of eligibility, asks follow-up questions,
    and guides the user based on rule engine results.
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        logger.info(
            "Processing intelligent chat request",
            extra={
                "event": "intelligent_chat_request",
                "session_id": session_id,
                "message_length": len(request.user_message)
            }
        )
        
        # Convert models to dicts for the service
        user_profile_dict = request.user_profile.model_dump()
        eligibility_results_dicts = [res.model_dump() for res in request.eligibility_results]
        
        response_data = await bedrock_service.get_response(
            session_id=session_id,
            user_message=request.user_message,
            user_profile=user_profile_dict,
            eligibility_results=eligibility_results_dicts
        )
        
        return ChatResponse(
            response_text=response_data.get("response_text", ""),
            missing_fields=response_data.get("missing_fields", []),
            recommended_next_step=response_data.get("recommended_next_step", ""),
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(
            "Failed to process intelligent chat",
            extra={
                "event": "intelligent_chat_error",
                "session_id": session_id,
                "error": str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error communicating with assistant"
        )
