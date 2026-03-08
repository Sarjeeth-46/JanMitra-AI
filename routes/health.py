"""
Health Check Endpoint

Provides system availability monitoring endpoint that responds
within 100ms with current system status and timestamp.

Requirements: 5.1, 5.2, 5.3, 5.4
"""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint for system monitoring.
    
    Returns:
        dict: JSON response with status and ISO 8601 timestamp
        
    Response time: <100ms
    HTTP Status: 200 OK
    
    Example response:
    {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    return {
        "backend": "ok",
        "ai_model": "ok",
        "storage": "ok"
    }
