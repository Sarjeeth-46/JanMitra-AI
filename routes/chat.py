"""
Chat Endpoint

Provides a conversational assistant endpoint that answers questions
about government schemes, eligibility, and the application process.
Uses a deterministic rule-based engine (no LLM).
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import logging

from slowapi import Limiter
from slowapi.util import get_remote_address
from middleware.auth import verify_token

from services.bedrock_service import BedrockService

bedrock_service = BedrockService()
router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


class ChatHistoryItem(BaseModel):
    """Single message in the chat history."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""
    message: str
    history: List[ChatHistoryItem] = []


class ChatResponse(BaseModel):
    """Response body for the /chat endpoint."""
    response: str


@router.post("/chat")
@limiter.limit("100/minute")
async def chat(request: Request, chat_request: ChatRequest, token: dict = Depends(verify_token)):
    """
    Chat with the JanMitra AI assistant using Bedrock Streaming.
    """
    if not chat_request.message or not chat_request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    try:
        history_dicts = [
            {"role": item.role, "content": item.content}
            for item in chat_request.history
        ]
        
        async def event_stream():
            async for chunk in bedrock_service.stream_chat(chat_request.message, history_dicts):
                yield chunk

        return StreamingResponse(event_stream(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )
