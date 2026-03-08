from pydantic import BaseModel
from typing import Optional, Dict, Any

class ApplicationSubmitRequest(BaseModel):
    scheme_id: str
    scheme_name: str
    user_profile: Dict[str, Any]

class ApplicationResponse(BaseModel):
    application_id: str
    scheme_name: str
    status: str
    submitted_date: str
    estimated_approval: str
