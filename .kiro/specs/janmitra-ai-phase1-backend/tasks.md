# Implementation Plan: JanMitra AI Phase 1 Backend

## Overview

This implementation plan breaks down the JanMitra AI Phase 1 Backend into discrete coding tasks. The system is a FastAPI-based government scheme eligibility evaluation service with DynamoDB storage and deterministic rule-based evaluation. Tasks are organized to build incrementally from data models through core services to API endpoints, with testing integrated throughout.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: routes/, services/, models/, database/, tests/
  - Create requirements.txt with FastAPI, Uvicorn, boto3, Pydantic, pytest, hypothesis
  - Create .env.example file for configuration template
  - Create main.py FastAPI application entry point
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [ ] 2. Implement data models
  - [x] 2.1 Create UserProfile model with Pydantic validation
    - Define UserProfile class in models/user_profile.py
    - Add field validations: name (min_length=1), age (0-150), income (>=0), state, occupation, category, land_size (>=0)
    - _Requirements: 2.2, 2.5_
  
  - [ ]* 2.2 Write property test for UserProfile validation
    - **Property 3: Profile Validation Completeness**
    - **Validates: Requirements 2.2, 2.5**
  
  - [ ]* 2.3 Write property test for JSON parsing round-trip
    - **Property 4: JSON Parsing Round-Trip**
    - **Validates: Requirements 2.3**
  
  - [x] 2.4 Create Scheme and EligibilityRule models
    - Define EligibilityRule class in models/scheme.py with fields: field, operator, value
    - Define Scheme class with fields: scheme_id, name, description, eligibility_rules
    - _Requirements: 1.2, 1.3_
  
  - [x] 2.5 Create EvaluationResult model
    - Define EvaluationResult class in models/evaluation_result.py
    - Include fields: scheme_name, eligible, missing_fields, failed_conditions
    - _Requirements: 4.2_
  
  - [x] 2.6 Create Settings configuration model
    - Define Settings class in models/config.py using pydantic_settings
    - Include: aws_region, dynamodb_table_name, api_port
    - Support loading from .env file
    - _Requirements: 6.4_

- [ ] 3. Implement rule engine core logic
  - [x] 3.1 Implement operator evaluation function
    - Create services/rule_engine.py
    - Implement apply_operator() supporting: equals, not_equals, less_than, less_than_or_equal, greater_than, greater_than_or_equal
    - _Requirements: 1.4, 3.3_
  
  - [ ]* 3.2 Write property test for operator correctness
    - **Property 2: Operator Correctness**
    - **Validates: Requirements 1.4, 3.3**
  
  - [x] 3.3 Implement single rule evaluation
    - Implement evaluate_rule() function that compares profile field against rule
    - Return tuple: (passed: bool, failed_condition_message: Optional[str])
    - Handle missing fields by returning appropriate message
    - _Requirements: 3.3, 3.6, 3.7_
  
  - [x] 3.4 Implement scheme evaluation function
    - Implement evaluate_scheme() that processes all rules for one scheme
    - Track missing_fields array for fields not present in profile
    - Track failed_conditions array for rules that don't pass
    - Determine eligible=true only when all rules pass
    - Return EvaluationResult object
    - _Requirements: 3.1, 3.4, 3.5, 3.6, 3.7_
  
  - [ ]* 3.5 Write property test for evaluation determinism
    - **Property 10: Evaluation Determinism**
    - **Validates: Requirements 3.8**
  
  - [ ]* 3.6 Write unit tests for rule engine
    - Test each operator with known values
    - Test missing field detection
    - Test failed condition tracking
    - Test empty rules array (should be eligible)
    - Test all rules pass vs some rules fail scenarios

- [x] 4. Checkpoint - Verify rule engine functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement DynamoDB repository layer
  - [x] 5.1 Create DynamoDB repository class
    - Create database/dynamodb_repository.py
    - Implement __init__() to initialize boto3 DynamoDB client
    - Read AWS credentials from environment variables
    - Use IAM role-based authentication (no hardcoded credentials)
    - _Requirements: 6.2, 6.3, 6.4, 6.5_
  
  - [x] 5.2 Implement get_all_schemes() method
    - Perform DynamoDB scan operation on government_schemes table
    - Parse items into Scheme objects
    - Handle empty table gracefully
    - _Requirements: 1.1, 1.2, 1.5_
  
  - [x] 5.3 Implement put_scheme() method
    - Store Scheme object to DynamoDB
    - Convert Scheme to DynamoDB item format
    - _Requirements: 1.2, 1.5_
  
  - [x] 5.4 Implement get_scheme_by_id() method
    - Retrieve single scheme by scheme_id partition key
    - Return None if not found
    - _Requirements: 1.2_
  
  - [ ]* 5.5 Write property test for scheme persistence round-trip
    - **Property 1: Scheme Persistence Round-Trip**
    - **Validates: Requirements 1.2**
  
  - [ ]* 5.6 Write unit tests for database operations
    - Test scheme retrieval with mocked DynamoDB
    - Test scheme storage
    - Test connection failure handling
    - Test retry logic for transient failures

- [ ] 6. Create seed data for 5 government schemes
  - [x] 6.1 Create database initialization script
    - Create database/seed_schemes.py script
    - Define all 5 schemes: PM-KISAN, Ayushman Bharat, Sukanya Samriddhi Yojana, MGNREGA, Stand Up India
    - Include scheme_id, name, description, and eligibility_rules for each
    - _Requirements: 1.1, 1.2, 1.3, 8.5_
  
  - [x] 6.2 Implement seed data loading function
    - Create function to load schemes into DynamoDB
    - Handle existing schemes (skip or update)
    - Provide CLI interface for running seed script
    - _Requirements: 1.1, 1.5_

- [ ] 7. Implement eligibility evaluation service
  - [x] 7.1 Create eligibility service orchestration
    - Create services/eligibility_service.py
    - Implement evaluate_eligibility() async function
    - Fetch all schemes from DynamoDB repository
    - Call rule engine's evaluate_scheme() for each scheme
    - _Requirements: 3.1, 4.1_
  
  - [x] 7.2 Implement result ranking function
    - Implement rank_results() to sort evaluation results
    - Place eligible=true schemes before eligible=false schemes
    - Secondary sort by scheme_name alphabetically
    - _Requirements: 4.3_
  
  - [ ]* 7.3 Write property test for complete scheme coverage
    - **Property 11: Complete Scheme Coverage**
    - **Validates: Requirements 4.1**
  
  - [ ]* 7.4 Write property test for eligible schemes ranked first
    - **Property 13: Eligible Schemes Ranked First**
    - **Validates: Requirements 4.3**
  
  - [ ]* 7.5 Write unit tests for eligibility service
    - Test evaluation with all schemes
    - Test ranking logic
    - Test with various user profiles (eligible/ineligible combinations)

- [ ] 8. Implement API endpoints
  - [x] 8.1 Create health check endpoint
    - Create routes/health.py
    - Implement GET /health endpoint
    - Return JSON: {"status": "healthy", "timestamp": "<ISO8601>"}
    - Ensure response time <100ms
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ]* 8.2 Write property test for health check response structure
    - **Property 15: Health Check Response Structure**
    - **Validates: Requirements 5.2, 5.4**
  
  - [x] 8.3 Create evaluation endpoint
    - Create routes/evaluation.py
    - Implement POST /evaluate endpoint
    - Accept UserProfile JSON in request body
    - Call eligibility_service.evaluate_eligibility()
    - Return ranked evaluation results as JSON array with HTTP 200
    - _Requirements: 2.1, 2.3, 4.1, 4.2, 4.4_
  
  - [x] 8.4 Add error handling for malformed requests
    - Customize FastAPI exception handler for validation errors
    - Return HTTP 400 with error description for invalid UserProfile
    - Handle malformed JSON gracefully
    - _Requirements: 2.4_
  
  - [ ]* 8.5 Write property test for malformed profile error response
    - **Property 5: Malformed Profile Error Response**
    - **Validates: Requirements 2.4**
  
  - [x] 8.6 Create schemes endpoint (optional)
    - Create routes/schemes.py
    - Implement GET /schemes endpoint
    - Return all stored schemes from DynamoDB
    - Useful for debugging and verification
  
  - [x] 8.7 Wire all routes to FastAPI application
    - Register all routers in main.py
    - Configure CORS if needed
    - Set up middleware for logging
    - _Requirements: 6.6, 7.2_
  
  - [ ]* 8.8 Write integration tests for API endpoints
    - Test /health endpoint
    - Test /evaluate with valid profile
    - Test /evaluate with missing fields
    - Test /evaluate with invalid JSON
    - Test /evaluate with wrong data types
    - Test /schemes endpoint

- [x] 9. Checkpoint - Verify API functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Add comprehensive error handling and logging
  - [x] 10.1 Implement structured logging
    - Configure Python logging module with JSON formatter
    - Add log statements at INFO, WARNING, ERROR levels
    - Log successful evaluations, validation failures, database errors
    - _Requirements: 3.2_
  
  - [-] 10.2 Add database error handling
    - Wrap DynamoDB operations in try-catch blocks
    - Implement retry logic with exponential backoff (max 3 retries)
    - Return HTTP 500 for database failures
  
  - [x] 10.3 Add service layer error handling
    - Handle unexpected exceptions in rule engine
    - Graceful degradation: continue evaluation if one scheme fails
    - Return partial results with error indicators

- [ ] 11. Create deployment and setup documentation
  - [x] 11.1 Create README.md with local setup instructions
    - Document Python version requirement (3.9+)
    - Document virtual environment setup
    - Document dependency installation (pip install -r requirements.txt)
    - Document environment variable configuration
    - Document DynamoDB Local setup for testing
    - Document running seed script to populate schemes
    - Document starting the server (uvicorn main:app --reload)
    - _Requirements: 8.1, 8.4_
  
  - [x] 11.2 Create AWS deployment documentation
    - Document EC2 t3.micro instance setup
    - Document IAM role creation with DynamoDB permissions
    - Document DynamoDB table creation (government_schemes)
    - Document environment variable configuration on EC2
    - Document systemd service setup for auto-start
    - Document security group configuration (port 8000)
    - _Requirements: 6.1, 6.2, 6.3, 6.6, 8.2_
  
  - [x] 11.3 Create API testing documentation
    - Provide example curl commands for /health endpoint
    - Provide example curl commands for /evaluate endpoint with sample profiles
    - Provide example responses for eligible and ineligible scenarios
    - Document expected response times
    - _Requirements: 8.3_

- [ ] 12. Performance validation and optimization
  - [ ]* 12.1 Write property test for evaluation performance
    - **Property 14: Evaluation Performance**
    - **Validates: Requirements 4.5**
  
  - [ ]* 12.2 Write property test for health check performance
    - **Property 16: Health Check Performance**
    - **Validates: Requirements 5.3**
  
  - [ ]* 12.3 Run performance tests
    - Verify /evaluate responds within 2 seconds
    - Verify /health responds within 100ms
    - Test with concurrent requests
    - Identify and optimize bottlenecks if needed

- [ ] 13. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout implementation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation uses Python with FastAPI framework as specified in the design
- All AWS credentials must be loaded from environment variables or IAM roles (no hardcoded secrets)
- DynamoDB table must be created before running the application
- Seed script must be run to populate the 5 government schemes before testing evaluation
