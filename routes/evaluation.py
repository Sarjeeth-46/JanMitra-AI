"""
Evaluation Endpoint

Provides the main eligibility evaluation endpoint that accepts user profile
data and returns ranked evaluation results for all government schemes.

Requirements: 2.1, 2.3, 4.1, 4.2, 4.4
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from models.user_profile import UserProfile
from models.evaluation_result import EvaluationResult
from services.eligibility_service import evaluate_eligibility
from typing import List
import logging

from slowapi import Limiter
from slowapi.util import get_remote_address
from middleware.auth import verify_token
from utils.masking import mask_income

router = APIRouter(tags=["evaluation"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

@router.post("/evaluate", response_model=List[EvaluationResult], status_code=status.HTTP_200_OK)
@limiter.limit("100/minute")
async def evaluate(request: Request, user_profile: UserProfile, token: dict = Depends(verify_token)):
    """
    Evaluate user eligibility across all government schemes.
    
    Accepts a UserProfile JSON object in the request body and returns
    a ranked list of evaluation results for all 5 government schemes.
    
    Args:
        user_profile: UserProfile object containing citizen information
            - name: User's full name (required, non-empty string)
            - age: User's age in years (required, 0-150)
            - income: Annual income in INR (required, >= 0)
            - state: State of residence (required, non-empty string)
            - occupation: Primary occupation (required, non-empty string)
            - category: Social category (required, e.g., General/OBC/SC/ST)
            - land_size: Land ownership in hectares (required, >= 0)
    
    Returns:
        List[EvaluationResult]: Ranked evaluation results with eligible schemes first
            Each result contains:
            - scheme_name: Name of the government scheme
            - eligible: Boolean indicating eligibility status
            - missing_fields: Array of missing profile fields (if any)
            - failed_conditions: Array of failed eligibility conditions (if any)
    
    HTTP Status:
        200 OK: Successful evaluation
        400 Bad Request: Invalid or malformed UserProfile (handled by FastAPI)
        500 Internal Server Error: Database or service errors
    
    Example request:
    {
        "name": "Rajesh Kumar",
        "age": 35,
        "income": 250000,
        "state": "Maharashtra",
        "occupation": "farmer",
        "category": "OBC",
        "land_size": 1.5
    }
    
    Example response:
    [
        {
            "scheme_name": "PM-KISAN",
            "eligible": true,
            "missing_fields": [],
            "failed_conditions": []
        },
        {
            "scheme_name": "Ayushman Bharat",
            "eligible": false,
            "missing_fields": [],
            "failed_conditions": ["income must be <= 500000"]
        }
    ]
    
    Requirements: 2.1, 2.3, 4.1, 4.2, 4.4
    """
    try:
        logger.info(
            "Starting eligibility evaluation",
            extra={
                "event": "evaluation_started",
                "user_age": user_profile.age,
                "user_state": user_profile.state,
                "user_category": user_profile.category,
                "user_income": mask_income(user_profile.income)
            }
        )
        
        # Call eligibility service to evaluate across all schemes
        results = await evaluate_eligibility(user_profile)
        
        # Count eligible schemes
        eligible_count = sum(1 for r in results if r.eligible)
        
        logger.info(
            "Eligibility evaluation completed successfully",
            extra={
                "event": "evaluation_completed",
                "total_schemes": len(results),
                "eligible_schemes": eligible_count,
            }
        )
        
        return results
        
    except Exception as e:
        logger.error(
            "Error during eligibility evaluation",
            extra={
                "event": "evaluation_error",
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during evaluation: {str(e)}"
        )
