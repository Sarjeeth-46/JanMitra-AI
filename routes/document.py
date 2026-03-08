"""
Document Upload Endpoint

Provides a document upload endpoint that accepts PDF, JPG, and PNG files,
extracts text from them, and returns structured profile data for auto-filling
the eligibility form.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import logging
import magic

from slowapi import Limiter
from slowapi.util import get_remote_address
from middleware.auth import verify_token

from services.document_extraction_service import TextractService

router = APIRouter(tags=["document"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

ALLOWED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]
ALLOWED_MIMETYPES = ["application/pdf", "image/jpeg", "image/png"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

textract_service = TextractService()

# In-memory dictionary to store document verification statuses for the demo
user_document_status: dict[str, dict[str, str]] = {}

@router.get("/documents/status")
@limiter.limit("50/minute")
async def get_document_status(request: Request, token: dict = Depends(verify_token)):
    email = token.get("sub", "anonymous")
    if email not in user_document_status:
        user_document_status[email] = {
            "aadhaar": "not_uploaded",
            "income_certificate": "not_uploaded"
        }
    return user_document_status[email]

@router.post("/upload-document")
@limiter.limit("50/minute")
async def upload_document(
    request: Request,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    token: dict = Depends(verify_token)
):
    """
    Unified endpoint for document upload.
    Processes either 'aadhaar' or 'income' based on document_type.
    """
    print(f"Uploading: {document_type}")
    print(f"File name: {file.filename}")
    
    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
        
    email = token.get("sub", "anonymous")
    if email not in user_document_status:
        user_document_status[email] = {"aadhaar": "not_uploaded", "income_certificate": "not_uploaded"}
    
    file_mime_type = magic.from_buffer(content, mime=True)
    if file_mime_type not in ["image/jpeg","image/png","application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    document_name = file.filename or "unknown"
    
    try:
        if document_type == "aadhaar":
            extraction_result = textract_service.extract_document_data(content)
            extracted_data = extraction_result.get("extracted_data", extraction_result.get("extracted_fields", {}))
            if not extracted_data.get("aadhaar"):
                user_document_status[email]["aadhaar"] = "failed"
                raise HTTPException(status_code=400, detail="Invalid document: Aadhaar number not found")
            user_document_status[email]["aadhaar"] = "verified"
        elif document_type == "income":
            extraction_result = textract_service.extract_income_data(content)
            extracted_data = extraction_result.get("extracted_data", {})
            if not extracted_data.get("annual_income"):
                 user_document_status[email]["income_certificate"] = "failed"
                 raise HTTPException(status_code=400, detail="Invalid document: Annual income not found")
            user_document_status[email]["income_certificate"] = "verified"
        else:
            raise HTTPException(status_code=400, detail="Invalid document type")

        return {
            "status": "success",
            "document_type": document_type,
            "data": extracted_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Textract failed for {document_name}", exc_info=True)
        doc_key = "aadhaar" if document_type == "aadhaar" else "income_certificate"
        user_document_status[email][doc_key] = "failed"
        raise HTTPException(status_code=500, detail="Extraction failure")
