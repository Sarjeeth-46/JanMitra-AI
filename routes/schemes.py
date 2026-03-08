"""
Schemes Endpoint

Provides a debugging endpoint to retrieve all stored government schemes
from DynamoDB. Useful for verification and debugging purposes.

This is an optional endpoint for Phase 1.
"""

from fastapi import APIRouter, HTTPException, status
from models.scheme import Scheme
from database.dynamodb_repository import DynamoDBRepository
from typing import List
import logging

router = APIRouter(tags=["schemes"])
logger = logging.getLogger(__name__)


@router.get("/schemes", response_model=List[Scheme], status_code=status.HTTP_200_OK)
async def get_schemes():
    """
    Retrieve all stored government schemes from DynamoDB.
    
    This endpoint is useful for debugging and verification purposes.
    It returns all schemes with their complete eligibility rules.
    
    Returns:
        List[Scheme]: All stored government schemes
            Each scheme contains:
            - scheme_id: Unique identifier for the scheme
            - name: Display name of the scheme
            - description: Detailed description of the scheme
            - eligibility_rules: Array of eligibility rule objects
                Each rule contains:
                - field: Field name from UserProfile to evaluate
                - operator: Comparison operator (equals, not_equals, less_than, etc.)
                - value: Value to compare against
    
    HTTP Status:
        200 OK: Successfully retrieved schemes
        500 Internal Server Error: Database or service errors
    
    Example response:
    [
        {
            "scheme_id": "PM_KISAN",
            "name": "PM-KISAN",
            "description": "Income support for farmer families",
            "eligibility_rules": [
                {
                    "field": "occupation",
                    "operator": "equals",
                    "value": "farmer"
                },
                {
                    "field": "land_size",
                    "operator": "less_than_or_equal",
                    "value": 2.0
                }
            ]
        }
    ]
    """
    try:
        logger.info("Fetching all schemes from DynamoDB")
        
        # Initialize repository and fetch all schemes
        repository = DynamoDBRepository()
        schemes = await repository.get_all_schemes()
        
        logger.info(f"Successfully retrieved {len(schemes)} schemes")
        
        return schemes
        
    except Exception as e:
        logger.error(f"Error fetching schemes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching schemes: {str(e)}"
        )
