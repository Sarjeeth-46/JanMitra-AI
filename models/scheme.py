from pydantic import BaseModel
from typing import List, Any


class EligibilityRule(BaseModel):
    """
    Represents a single eligibility rule for a government scheme.
    
    Attributes:
        field: Field name from UserProfile to evaluate (e.g., 'age', 'income', 'occupation')
        operator: Comparison operator - one of: equals, not_equals, less_than, 
                  less_than_or_equal, greater_than, greater_than_or_equal
        value: Value to compare against (can be string, number, or other types)
    """
    field: str
    operator: str
    value: Any


class Scheme(BaseModel):
    """
    Represents a government scheme with eligibility criteria.
    
    Attributes:
        scheme_id: Unique identifier for the scheme (e.g., 'PM_KISAN')
        name: Display name of the scheme (e.g., 'PM-KISAN')
        description: Brief description of the scheme's purpose
        eligibility_rules: List of rules that must all pass for eligibility
    """
    scheme_id: str
    name: str
    description: str
    eligibility_rules: List[EligibilityRule]
