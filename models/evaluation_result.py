from pydantic import BaseModel
from typing import List, Optional


class EvaluationResult(BaseModel):
    scheme_name: str
    eligible: bool
    missing_fields: List[str] = []
    failed_conditions: List[str] = []
    scheme_id: Optional[str] = None
    scheme_description: Optional[str] = None
