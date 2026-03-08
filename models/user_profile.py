from pydantic import BaseModel, Field, validator

class UserProfile(BaseModel):
    """User profile model for government scheme eligibility evaluation.
    
    Contains demographic and socioeconomic information required to evaluate
    eligibility across various government schemes.
    """
    name: str = Field(..., min_length=1, description="User's full name")
    age: int = Field(..., description="User's age in years")
    income: float = Field(..., ge=0, description="Annual income in INR")
    state: str = Field(..., min_length=1, description="State of residence")
    occupation: str = Field(..., min_length=1, description="Primary occupation")
    category: str = Field(..., description="Social category (General/OBC/SC/ST)")
    land_size: float = Field(..., ge=0, description="Land ownership in hectares")

    @validator("age")
    def validate_age(cls, value):
        if value < 18 or value > 120:
            raise ValueError("Age must be between 18 and 120")
        return value
