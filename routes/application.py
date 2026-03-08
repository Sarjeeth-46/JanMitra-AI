from fastapi import APIRouter, HTTPException, status, Depends, Request
from models.application import ApplicationSubmitRequest, ApplicationResponse
from database.application_repository import ApplicationRepository
from middleware.auth import verify_token
import logging

router = APIRouter(tags=["application"])
logger = logging.getLogger(__name__)
app_repo = ApplicationRepository()

@router.post("/submit-application", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def submit_application(request: Request, body: ApplicationSubmitRequest, token: dict = Depends(verify_token)):
    """
    Submit a new government scheme application.
    """
    email = token.get("sub")
    
    try:
        # Prepare application data
        application_data = {
            "user_email": email,
            "scheme_id": body.scheme_id,
            "scheme_name": body.scheme_name,
            "applicant_name": body.user_profile.get("name", "User"),
            "applicant_phone": body.user_profile.get("phone", "N/A"),
            "user_profile": body.user_profile
        }
        
        logger.info(f"Submitting application for {email} for scheme {body.scheme_name}")
        new_app = await app_repo.create_application(application_data)
        
        # Clear document verification status so the user can apply for another scheme cleanly
        from routes.document import user_document_status
        if email in user_document_status:
            user_document_status[email] = {
                "aadhaar": "not_uploaded",
                "income_certificate": "not_uploaded"
            }
        
        return ApplicationResponse(
            application_id=new_app['application_id'],
            scheme_name=new_app['scheme_name'],
            status=new_app['status'],
            submitted_date=new_app['submitted_date'],
            estimated_approval=new_app['estimated_approval']
        )
        
    except Exception as e:
        logger.error(f"Failed to submit application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit application: {str(e)}"
        )
