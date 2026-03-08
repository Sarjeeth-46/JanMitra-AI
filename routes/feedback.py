"""
Feedback Route

Accepts user feedback submissions.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
import logging

router = APIRouter(tags=["feedback"])
logger = logging.getLogger(__name__)


class FeedbackRequest(BaseModel):
    name: str
    email: str
    message: str


@router.post("/feedback", status_code=status.HTTP_200_OK)
async def submit_feedback(body: FeedbackRequest):
    """Accept and log user feedback."""
    logger.info(
        "Feedback received",
        extra={
            "event": "feedback_submitted",
            "name": body.name,
            "email": body.email,
            "message_length": len(body.message),
        }
    )
    return {"message": "Thank you for your feedback! We will get back to you soon."}
