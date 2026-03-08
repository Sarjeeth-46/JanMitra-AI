# Requirements Document

## Introduction

JanMitra AI Phase 1 Backend is a government scheme eligibility evaluation system designed for the AI for Bharat hackathon. This phase focuses on building a solid backend foundation with deterministic rule-based eligibility evaluation. The system stores government schemes with structured eligibility rules, accepts user profile data, evaluates eligibility without LLM involvement, and returns ranked results via REST API. This is a 2-day foundation (Day 1-2 of 7-day hackathon) that will be deployed on AWS EC2 with DynamoDB storage.

## Glossary

- **Backend_System**: The FastAPI-based server application that processes eligibility requests
- **Rule_Engine**: The deterministic evaluation component that processes eligibility rules against user profiles
- **Scheme**: A government benefit program with defined eligibility criteria
- **User_Profile**: A structured data object containing citizen information (name, age, income, state, occupation, category, land_size)
- **Eligibility_Rule**: A structured JSON condition that defines one criterion for scheme qualification
- **DynamoDB_Store**: The AWS DynamoDB database that persists scheme data
- **API_Endpoint**: A REST HTTP endpoint exposed by the Backend_System
- **Evaluation_Result**: A structured response containing eligibility status, missing fields, and failed conditions

## Requirements

### Requirement 1: Store Government Schemes

**User Story:** As a system administrator, I want to store government schemes with structured eligibility rules, so that the system can evaluate citizen eligibility

#### Acceptance Criteria

1. THE DynamoDB_Store SHALL store exactly 5 government schemes for Phase 1
2. WHEN a Scheme is stored, THE DynamoDB_Store SHALL persist the scheme name, description, and eligibility rules array
3. THE Backend_System SHALL define Eligibility_Rule format with fields: field, operator, and value
4. THE Backend_System SHALL support operators: equals, not_equals, less_than, less_than_or_equal, greater_than, greater_than_or_equal
5. FOR ALL stored Schemes, THE DynamoDB_Store SHALL maintain data integrity and availability

### Requirement 2: Accept User Profile Data

**User Story:** As a citizen, I want to submit my profile information, so that the system can evaluate my eligibility for government schemes

#### Acceptance Criteria

1. THE API_Endpoint SHALL accept User_Profile data via POST request to /evaluate
2. THE Backend_System SHALL validate User_Profile contains fields: name, age, income, state, occupation, category, land_size
3. WHEN User_Profile data is received, THE Backend_System SHALL parse and validate JSON format
4. IF User_Profile is malformed, THEN THE Backend_System SHALL return HTTP 400 with error description
5. THE Backend_System SHALL accept numeric values for age, income, and land_size fields

### Requirement 3: Evaluate Eligibility Deterministically

**User Story:** As a system operator, I want eligibility evaluation to be deterministic and rule-based, so that results are consistent and explainable without LLM involvement

#### Acceptance Criteria

1. THE Rule_Engine SHALL evaluate all Eligibility_Rules for each Scheme against the User_Profile
2. THE Rule_Engine SHALL NOT use any LLM or AI model for eligibility logic
3. WHEN evaluating a rule, THE Rule_Engine SHALL compare User_Profile field values using the specified operator
4. THE Rule_Engine SHALL determine eligibility as true when all rules pass for a Scheme
5. THE Rule_Engine SHALL determine eligibility as false when any rule fails for a Scheme
6. WHEN a User_Profile field is missing, THE Rule_Engine SHALL record it in missing_fields array
7. WHEN a rule evaluation fails, THE Rule_Engine SHALL record the failed condition in failed_conditions array
8. FOR ALL evaluations with identical User_Profile and Scheme data, THE Rule_Engine SHALL produce identical Evaluation_Results

### Requirement 4: Return Ranked Eligibility Results

**User Story:** As a citizen, I want to receive ranked eligibility results, so that I know which schemes I qualify for and why

#### Acceptance Criteria

1. WHEN evaluation completes, THE Backend_System SHALL return Evaluation_Result for all 5 Schemes
2. THE Evaluation_Result SHALL include fields: scheme_name, eligible (boolean), missing_fields (array), failed_conditions (array)
3. THE Backend_System SHALL rank Schemes with eligible=true before eligible=false
4. THE Backend_System SHALL return results as JSON array via HTTP 200 response
5. THE Backend_System SHALL complete evaluation and return results within 2 seconds

### Requirement 5: Provide Health Check Endpoint

**User Story:** As a DevOps engineer, I want a health check endpoint, so that I can monitor system availability

#### Acceptance Criteria

1. THE API_Endpoint SHALL respond to GET requests at /health
2. WHEN the Backend_System is operational, THE API_Endpoint SHALL return HTTP 200 with status "healthy"
3. THE API_Endpoint SHALL respond to health checks within 100 milliseconds
4. THE Backend_System SHALL include timestamp in health check response

### Requirement 6: Support AWS Deployment

**User Story:** As a DevOps engineer, I want the system deployable on AWS infrastructure, so that it runs as a live hosted prototype

#### Acceptance Criteria

1. THE Backend_System SHALL run on AWS EC2 t3.micro instance
2. THE Backend_System SHALL connect to DynamoDB using boto3 library
3. THE Backend_System SHALL authenticate to AWS services using IAM role-based access
4. THE Backend_System SHALL read AWS credentials from environment variables
5. THE Backend_System SHALL NOT contain hardcoded secrets or credentials
6. THE Backend_System SHALL expose API endpoints on port 8000

### Requirement 7: Maintain Modular Code Structure

**User Story:** As a developer, I want clean modular code structure, so that the system is maintainable and extensible

#### Acceptance Criteria

1. THE Backend_System SHALL organize code into separate directories: routes, services, models, database
2. THE Backend_System SHALL implement API routes in the routes directory
3. THE Backend_System SHALL implement business logic in the services directory
4. THE Backend_System SHALL define data models in the models directory
5. THE Backend_System SHALL implement database operations in the database directory
6. THE Backend_System SHALL use Python with FastAPI framework
7. THE Backend_System SHALL include requirements.txt with all dependencies

### Requirement 8: Provide Setup and Testing Documentation

**User Story:** As a developer, I want setup and testing instructions, so that I can run and verify the system locally

#### Acceptance Criteria

1. THE Backend_System SHALL include step-by-step local setup instructions
2. THE Backend_System SHALL include AWS deployment instructions for EC2
3. THE Backend_System SHALL provide example curl commands for testing API endpoints
4. THE Backend_System SHALL document DynamoDB table schema and setup
5. THE Backend_System SHALL include example rule JSON for all 5 government schemes
