# Design Document: JanMitra AI Phase 1 Backend

## Overview

JanMitra AI Phase 1 Backend is a deterministic government scheme eligibility evaluation system built for rapid deployment in a hackathon environment. The system uses FastAPI for REST API endpoints, DynamoDB for scheme storage, and a pure rule-based engine for eligibility evaluation without any LLM involvement.

The architecture prioritizes simplicity, determinism, and explainability. All eligibility decisions are made through structured JSON rules evaluated against user profile data, ensuring consistent and auditable results. The system is designed for AWS EC2 deployment with DynamoDB as the persistence layer.

Key design principles:
- **Deterministic evaluation**: No AI/LLM involvement, pure rule-based logic
- **Explainable results**: Every decision includes missing fields and failed conditions
- **Rapid deployment**: Minimal dependencies, straightforward AWS setup
- **Modular structure**: Clear separation between routes, services, models, and database layers

## Architecture

### System Architecture

The system follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────┐
│                     Client (Citizen)                     │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   /health    │  │  /evaluate   │  │  /schemes    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Eligibility Evaluation Service           │   │
│  │  - Profile validation                            │   │
│  │  - Rule engine orchestration                     │   │
│  │  - Result ranking                                │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Rule Engine                         │   │
│  │  - Operator evaluation (==, !=, <, <=, >, >=)   │   │
│  │  - Missing field detection                       │   │
│  │  - Failed condition tracking                     │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Database Layer                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         DynamoDB Repository                      │   │
│  │  - Scheme CRUD operations                        │   │
│  │  - Connection management                         │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ boto3
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AWS DynamoDB                                │
│              Table: government_schemes                   │
└─────────────────────────────────────────────────────────┘
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Cloud                             │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         EC2 Instance (t3.micro)                │    │
│  │                                                 │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │   FastAPI Application (Port 8000)        │  │    │
│  │  │   - Uvicorn ASGI Server                  │  │    │
│  │  │   - Python 3.9+                          │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  │                                                 │    │
│  │  IAM Role: janmitra-ec2-role                   │    │
│  │  - DynamoDB read/write permissions             │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                     │
│                   │ boto3 SDK                           │
│                   ▼                                     │
│  ┌────────────────────────────────────────────────┐    │
│  │         DynamoDB                               │    │
│  │         Table: government_schemes              │    │
│  │         - Partition Key: scheme_id (String)    │    │
│  │         - Billing: On-Demand                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Web Framework**: FastAPI 0.104+ (async support, automatic OpenAPI docs)
- **ASGI Server**: Uvicorn (production-ready async server)
- **Database**: AWS DynamoDB (serverless, scalable NoSQL)
- **AWS SDK**: boto3 3.28+ (DynamoDB client)
- **Python Version**: 3.9+ (type hints, async/await support)
- **Validation**: Pydantic 2.0+ (data validation via FastAPI)
- **Deployment**: AWS EC2 t3.micro, IAM role-based authentication

## Components and Interfaces

### API Layer Components

#### Health Check Endpoint

**Route**: `GET /health`

**Purpose**: System availability monitoring

**Response Schema**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Implementation**: `routes/health.py`

#### Evaluation Endpoint

**Route**: `POST /evaluate`

**Purpose**: Evaluate user eligibility across all schemes

**Request Schema**:
```json
{
  "name": "string",
  "age": "integer",
  "income": "number",
  "state": "string",
  "occupation": "string",
  "category": "string",
  "land_size": "number"
}
```

**Response Schema**:
```json
[
  {
    "scheme_name": "string",
    "eligible": "boolean",
    "missing_fields": ["string"],
    "failed_conditions": ["string"]
  }
]
```

**Implementation**: `routes/evaluation.py`

#### Schemes Endpoint (Optional for Phase 1)

**Route**: `GET /schemes`

**Purpose**: Retrieve all stored schemes (useful for debugging)

**Response Schema**:
```json
[
  {
    "scheme_id": "string",
    "name": "string",
    "description": "string",
    "eligibility_rules": [
      {
        "field": "string",
        "operator": "string",
        "value": "any"
      }
    ]
  }
]
```

### Service Layer Components

#### Eligibility Evaluation Service

**Module**: `services/eligibility_service.py`

**Responsibilities**:
- Orchestrate the evaluation workflow
- Fetch all schemes from database
- Validate user profile completeness
- Invoke rule engine for each scheme
- Rank results (eligible schemes first)
- Format response

**Key Methods**:
```python
async def evaluate_eligibility(user_profile: UserProfile) -> List[EvaluationResult]:
    """
    Evaluate user eligibility across all schemes.
    Returns ranked list of evaluation results.
    """
    pass

def rank_results(results: List[EvaluationResult]) -> List[EvaluationResult]:
    """
    Sort results with eligible=True first, then by scheme name.
    """
    pass
```

#### Rule Engine

**Module**: `services/rule_engine.py`

**Responsibilities**:
- Evaluate individual eligibility rules
- Support all comparison operators
- Track missing fields
- Track failed conditions
- Ensure deterministic evaluation

**Key Methods**:
```python
def evaluate_scheme(scheme: Scheme, user_profile: UserProfile) -> EvaluationResult:
    """
    Evaluate all rules for a single scheme.
    Returns evaluation result with eligibility status and details.
    """
    pass

def evaluate_rule(rule: EligibilityRule, user_profile: UserProfile) -> Tuple[bool, Optional[str]]:
    """
    Evaluate a single rule against user profile.
    Returns (passed, failed_condition_message).
    """
    pass

def apply_operator(operator: str, profile_value: Any, rule_value: Any) -> bool:
    """
    Apply comparison operator to values.
    Supports: equals, not_equals, less_than, less_than_or_equal, 
              greater_than, greater_than_or_equal
    """
    pass
```

**Operator Implementation**:
- `equals`: `profile_value == rule_value`
- `not_equals`: `profile_value != rule_value`
- `less_than`: `profile_value < rule_value`
- `less_than_or_equal`: `profile_value <= rule_value`
- `greater_than`: `profile_value > rule_value`
- `greater_than_or_equal`: `profile_value >= rule_value`

### Database Layer Components

#### DynamoDB Repository

**Module**: `database/dynamodb_repository.py`

**Responsibilities**:
- Manage DynamoDB connection
- Perform CRUD operations on schemes
- Handle AWS authentication
- Manage connection lifecycle

**Key Methods**:
```python
class DynamoDBRepository:
    def __init__(self, table_name: str = "government_schemes"):
        """Initialize DynamoDB client using boto3."""
        pass
    
    async def get_all_schemes(self) -> List[Scheme]:
        """Retrieve all schemes from DynamoDB."""
        pass
    
    async def get_scheme_by_id(self, scheme_id: str) -> Optional[Scheme]:
        """Retrieve a single scheme by ID."""
        pass
    
    async def put_scheme(self, scheme: Scheme) -> None:
        """Store or update a scheme in DynamoDB."""
        pass
```

**DynamoDB Table Schema**:
- **Table Name**: `government_schemes`
- **Partition Key**: `scheme_id` (String)
- **Attributes**:
  - `scheme_id`: Unique identifier (e.g., "PM_KISAN")
  - `name`: Display name (e.g., "PM-KISAN")
  - `description`: Scheme description
  - `eligibility_rules`: List of rule objects (stored as JSON)

**Example DynamoDB Item**:
```json
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
```

## Data Models

### UserProfile Model

**Module**: `models/user_profile.py`

```python
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    name: str = Field(..., min_length=1, description="User's full name")
    age: int = Field(..., ge=0, le=150, description="User's age in years")
    income: float = Field(..., ge=0, description="Annual income in INR")
    state: str = Field(..., min_length=1, description="State of residence")
    occupation: str = Field(..., min_length=1, description="Primary occupation")
    category: str = Field(..., description="Social category (General/OBC/SC/ST)")
    land_size: float = Field(..., ge=0, description="Land ownership in hectares")
```

### Scheme Model

**Module**: `models/scheme.py`

```python
from pydantic import BaseModel
from typing import List

class EligibilityRule(BaseModel):
    field: str  # Field name from UserProfile
    operator: str  # One of: equals, not_equals, less_than, etc.
    value: Any  # Value to compare against

class Scheme(BaseModel):
    scheme_id: str
    name: str
    description: str
    eligibility_rules: List[EligibilityRule]
```

### EvaluationResult Model

**Module**: `models/evaluation_result.py`

```python
from pydantic import BaseModel
from typing import List

class EvaluationResult(BaseModel):
    scheme_name: str
    eligible: bool
    missing_fields: List[str] = []
    failed_conditions: List[str] = []
```

### Configuration Model

**Module**: `models/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_region: str = "ap-south-1"
    dynamodb_table_name: str = "government_schemes"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
```

## Data Models (Continued)

### Five Government Schemes for Phase 1

The system will store these 5 schemes in DynamoDB:

1. **PM-KISAN** (Pradhan Mantri Kisan Samman Nidhi)
   - Target: Small and marginal farmers
   - Rules: occupation=farmer, land_size<=2.0

2. **Ayushman Bharat** (PM-JAY)
   - Target: Low-income families
   - Rules: income<=500000, category in [SC, ST, OBC]

3. **Sukanya Samriddhi Yojana**
   - Target: Girl child savings
   - Rules: age<=10, (parent occupation or guardian)

4. **MGNREGA** (Mahatma Gandhi National Rural Employment Guarantee Act)
   - Target: Rural households
   - Rules: state not in [Delhi, Mumbai, Bangalore], income<=300000

5. **Stand Up India**
   - Target: SC/ST/Women entrepreneurs
   - Rules: age>=18, age<=65, category in [SC, ST] OR gender=female


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Scheme Persistence Round-Trip

*For any* valid Scheme object with scheme_id, name, description, and eligibility_rules, storing it to DynamoDB and then retrieving it should return an equivalent Scheme object with all fields preserved.

**Validates: Requirements 1.2**

### Property 2: Operator Correctness

*For any* two comparable values and any supported operator (equals, not_equals, less_than, less_than_or_equal, greater_than, greater_than_or_equal), applying the operator should produce the mathematically correct boolean result.

**Validates: Requirements 1.4, 3.3**

### Property 3: Profile Validation Completeness

*For any* UserProfile object, validation should pass if and only if all required fields (name, age, income, state, occupation, category, land_size) are present with correct types (strings for text fields, numeric for age/income/land_size).

**Validates: Requirements 2.2, 2.5**

### Property 4: JSON Parsing Round-Trip

*For any* valid UserProfile object, serializing it to JSON and then parsing it back should produce an equivalent UserProfile object.

**Validates: Requirements 2.3**

### Property 5: Malformed Profile Error Response

*For any* malformed or invalid UserProfile (missing required fields, wrong types, invalid JSON), the API should return HTTP 400 status with an error description.

**Validates: Requirements 2.4**

### Property 6: All Rules Evaluated

*For any* Scheme and UserProfile, the evaluation result should reflect the outcome of all eligibility rules in the scheme (either all passed, or specific rules appear in failed_conditions).

**Validates: Requirements 3.1**

### Property 7: Eligibility Determined by Rule Conjunction

*For any* Scheme and UserProfile, the eligible field should be true if and only if all eligibility rules pass for that profile.

**Validates: Requirements 3.4, 3.5**

### Property 8: Missing Fields Tracked

*For any* UserProfile with missing fields and any Scheme with rules referencing those fields, the missing fields should be recorded in the missing_fields array of the evaluation result.

**Validates: Requirements 3.6**

### Property 9: Failed Conditions Tracked

*For any* Scheme rule that fails evaluation against a UserProfile, a description of the failed condition should appear in the failed_conditions array.

**Validates: Requirements 3.7**

### Property 10: Evaluation Determinism

*For any* UserProfile and Scheme, evaluating the same profile against the same scheme multiple times should always produce identical EvaluationResult objects (same eligible status, same missing_fields, same failed_conditions).

**Validates: Requirements 3.8**

### Property 11: Complete Scheme Coverage

*For any* evaluation request, the response should contain exactly one EvaluationResult for each of the 5 stored government schemes.

**Validates: Requirements 4.1**

### Property 12: Response Structure Completeness

*For any* evaluation response, each EvaluationResult should be a valid JSON object containing scheme_name (string), eligible (boolean), missing_fields (array), and failed_conditions (array), and the overall response should be a JSON array with HTTP 200 status.

**Validates: Requirements 4.2, 4.4**

### Property 13: Eligible Schemes Ranked First

*For any* evaluation response containing both eligible and ineligible schemes, all schemes with eligible=true should appear before all schemes with eligible=false in the results array.

**Validates: Requirements 4.3**

### Property 14: Evaluation Performance

*For any* valid UserProfile evaluation request, the system should return results within 2 seconds.

**Validates: Requirements 4.5**

### Property 15: Health Check Response Structure

*For any* GET request to /health when the system is operational, the response should be HTTP 200 with a JSON object containing status="healthy" and a valid ISO 8601 timestamp.

**Validates: Requirements 5.2, 5.4**

### Property 16: Health Check Performance

*For any* health check request, the system should respond within 100 milliseconds.

**Validates: Requirements 5.3**

## Error Handling

### Error Categories

The system handles four primary error categories:

1. **Validation Errors** (HTTP 400)
   - Missing required fields in UserProfile
   - Invalid data types (non-numeric age, income, land_size)
   - Malformed JSON in request body
   - Empty or whitespace-only string fields

2. **Database Errors** (HTTP 500)
   - DynamoDB connection failures
   - AWS authentication failures
   - Table not found errors
   - Read/write operation failures

3. **System Errors** (HTTP 500)
   - Unexpected exceptions in rule engine
   - Service layer failures
   - Unhandled edge cases

4. **Not Found Errors** (HTTP 404)
   - Invalid API endpoints
   - Scheme not found (if querying specific scheme)

### Error Response Format

All errors return a consistent JSON structure:

```json
{
  "error": "error_category",
  "message": "Human-readable error description",
  "details": {
    "field": "specific_field_name",
    "reason": "detailed_reason"
  }
}
```

### Error Handling Strategy

**Validation Layer**:
- Pydantic models automatically validate request data
- FastAPI returns 422 for validation failures (we'll customize to 400)
- Custom validators for business logic constraints

**Service Layer**:
- Try-catch blocks around rule engine operations
- Graceful degradation: if one scheme evaluation fails, continue with others
- Log all errors with context for debugging

**Database Layer**:
- Retry logic for transient DynamoDB failures (max 3 retries with exponential backoff)
- Connection pooling to prevent resource exhaustion
- Fallback to cached scheme data if DynamoDB is temporarily unavailable (optional for Phase 1)

**Logging Strategy**:
- Use Python's logging module with structured JSON logs
- Log levels:
  - INFO: Successful evaluations, health checks
  - WARNING: Validation failures, missing fields
  - ERROR: Database failures, unexpected exceptions
  - DEBUG: Rule evaluation details (disabled in production)

### Edge Cases

1. **Empty eligibility rules**: Scheme with no rules should evaluate as eligible=true for all profiles
2. **Null/None values**: Treat as missing fields, not as valid values
3. **Case sensitivity**: Field names and operators are case-sensitive; state names are case-insensitive
4. **Numeric comparisons**: Handle both integers and floats consistently
5. **Zero values**: Zero is a valid value for income and land_size (different from missing)

## Testing Strategy

### Dual Testing Approach

The system requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples demonstrating correct behavior
- Edge cases (empty rules, zero values, boundary conditions)
- Error conditions (malformed input, database failures)
- Integration points between layers

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must always be maintained
- Round-trip properties (serialization, parsing)

Both approaches are complementary and necessary. Unit tests catch concrete bugs and verify specific scenarios, while property tests verify general correctness across a wide input space.

### Property-Based Testing Configuration

**Framework**: Use `hypothesis` library for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: janmitra-ai-phase1-backend, Property {number}: {property_text}`

**Example Property Test Structure**:

```python
from hypothesis import given, strategies as st
import hypothesis

# Feature: janmitra-ai-phase1-backend, Property 2: Operator Correctness
@given(
    value1=st.floats(allow_nan=False, allow_infinity=False),
    value2=st.floats(allow_nan=False, allow_infinity=False),
    operator=st.sampled_from(['equals', 'not_equals', 'less_than', 
                              'less_than_or_equal', 'greater_than', 
                              'greater_than_or_equal'])
)
@hypothesis.settings(max_examples=100)
def test_operator_correctness(value1, value2, operator):
    result = apply_operator(operator, value1, value2)
    
    if operator == 'equals':
        assert result == (value1 == value2)
    elif operator == 'not_equals':
        assert result == (value1 != value2)
    elif operator == 'less_than':
        assert result == (value1 < value2)
    # ... etc
```

### Unit Testing Strategy

**Test Organization**:
```
tests/
├── unit/
│   ├── test_rule_engine.py
│   ├── test_eligibility_service.py
│   ├── test_models.py
│   └── test_operators.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   └── test_end_to_end.py
└── property/
    ├── test_properties_rule_engine.py
    ├── test_properties_validation.py
    └── test_properties_persistence.py
```

**Key Unit Test Cases**:

1. **Rule Engine Tests**:
   - Test each operator with known values
   - Test missing field detection
   - Test failed condition tracking
   - Test empty rules array
   - Test all rules pass scenario
   - Test some rules fail scenario

2. **API Endpoint Tests**:
   - Test /health returns 200 with correct structure
   - Test /evaluate with valid profile
   - Test /evaluate with missing fields
   - Test /evaluate with invalid JSON
   - Test /evaluate with wrong data types

3. **Database Tests**:
   - Test scheme retrieval
   - Test scheme storage
   - Test connection failure handling
   - Test retry logic

4. **Integration Tests**:
   - Test full evaluation flow with all 5 schemes
   - Test ranking of results
   - Test performance requirements
   - Test concurrent requests

**Test Data**:
- Create fixtures for the 5 government schemes
- Create sample user profiles (eligible and ineligible for each scheme)
- Use factories for generating test data variations

**Mocking Strategy**:
- Mock DynamoDB calls in unit tests
- Use real DynamoDB Local for integration tests
- Mock AWS credentials in test environment

### Coverage Goals

- Line coverage: >85%
- Branch coverage: >80%
- Critical paths (rule engine, evaluation service): 100%

### Continuous Testing

- Run unit tests on every commit
- Run property tests on every pull request
- Run integration tests before deployment
- Performance tests in staging environment

