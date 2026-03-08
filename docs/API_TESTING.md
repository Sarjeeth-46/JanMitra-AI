# API Testing Documentation

This document provides comprehensive examples for testing the JanMitra AI Phase 1 Backend API endpoints using curl commands. All examples include sample requests, expected responses, and performance benchmarks.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Health Check Endpoint](#health-check-endpoint)
- [Evaluation Endpoint](#evaluation-endpoint)
- [Schemes Endpoint](#schemes-endpoint)
- [Performance Expectations](#performance-expectations)
- [Error Scenarios](#error-scenarios)

## Prerequisites

Before testing the API, ensure:

1. The server is running on `http://localhost:8000` (or your deployment URL)
2. DynamoDB is accessible and contains the 5 government schemes
3. You have `curl` installed on your system
4. For timing tests, use `curl` with the `-w` flag to measure response times

**Starting the server locally:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Health Check Endpoint

### Basic Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify system availability and operational status

**Expected Response Time:** < 100ms

**Example Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response (HTTP 200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45Z"
}
```

### Health Check with Timing

To measure response time:

```bash
curl -X GET http://localhost:8000/health \
  -w "\nTime: %{time_total}s\n" \
  -o /dev/null -s
```

**Expected Output:**
```
Time: 0.015s
```

### Health Check with Full Details

```bash
curl -X GET http://localhost:8000/health -v
```

This will show full HTTP headers and response details.

---

## Evaluation Endpoint

### Basic Evaluation Request

**Endpoint:** `POST /evaluate`

**Purpose:** Evaluate user eligibility across all 5 government schemes

**Expected Response Time:** < 2 seconds

**Content-Type:** `application/json`

### Example 1: Eligible Farmer Profile

This profile should be eligible for PM-KISAN (farmer with ≤2 hectares land).

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rajesh Kumar",
    "age": 35,
    "income": 250000,
    "state": "Maharashtra",
    "occupation": "farmer",
    "category": "OBC",
    "land_size": 1.5
  }'
```

**Expected Response (HTTP 200):**
```json
[
  {
    "scheme_name": "PM-KISAN",
    "eligible": true,
    "missing_fields": [],
    "failed_conditions": []
  },
  {
    "scheme_name": "Stand Up India",
    "eligible": true,
    "missing_fields": [],
    "failed_conditions": []
  },
  {
    "scheme_name": "Ayushman Bharat",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "income must be <= 500000"
    ]
  },
  {
    "scheme_name": "MGNREGA",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "income must be <= 300000"
    ]
  },
  {
    "scheme_name": "Sukanya Samriddhi Yojana",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "age must be <= 10"
    ]
  }
]
```

**Note:** Eligible schemes appear first in the response (ranked).

### Example 2: Low-Income Profile (Multiple Eligible Schemes)

This profile should be eligible for multiple schemes due to low income.

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Sharma",
    "age": 28,
    "income": 180000,
    "state": "Uttar Pradesh",
    "occupation": "laborer",
    "category": "SC",
    "land_size": 0.0
  }'
```

**Expected Response (HTTP 200):**
```json
[
  {
    "scheme_name": "Ayushman Bharat",
    "eligible": true,
    "missing_fields": [],
    "failed_conditions": []
  },
  {
    "scheme_name": "MGNREGA",
    "eligible": true,
    "missing_fields": [],
    "failed_conditions": []
  },
  {
    "scheme_name": "Stand Up India",
    "eligible": true,
    "missing_fields": [],
    "failed_conditions": []
  },
  {
    "scheme_name": "PM-KISAN",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "occupation must be equals farmer"
    ]
  },
  {
    "scheme_name": "Sukanya Samriddhi Yojana",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "age must be <= 10"
    ]
  }
]
```

### Example 3: Young Child Profile (Sukanya Samriddhi Eligible)

This profile represents a girl child eligible for Sukanya Samriddhi Yojana.

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ananya Patel",
    "age": 8,
    "income": 450000,
    "state": "Gujarat",
    "occupation": "student",
    "category": "General",
    "land_size": 0.0
  }'
```

**Expected Response (HTTP 200):**
```json
[
  {
    "scheme_name": "Sukanya Samriddhi Yojana",
    "eligible": true,
    "missing_fields": [],
    "failed_conditions": []
  },
  {
    "scheme_name": "Ayushman Bharat",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "income must be <= 500000"
    ]
  },
  {
    "scheme_name": "MGNREGA",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "income must be <= 300000"
    ]
  },
  {
    "scheme_name": "PM-KISAN",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "occupation must be equals farmer"
    ]
  },
  {
    "scheme_name": "Stand Up India",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "age must be >= 18"
    ]
  }
]
```

### Example 4: High-Income Profile (No Eligible Schemes)

This profile has high income and doesn't qualify for any schemes.

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vikram Singh",
    "age": 45,
    "income": 1200000,
    "state": "Karnataka",
    "occupation": "engineer",
    "category": "General",
    "land_size": 0.0
  }'
```

**Expected Response (HTTP 200):**
```json
[
  {
    "scheme_name": "Stand Up India",
    "eligible": true,
    "missing_fields": [],
    "failed_conditions": []
  },
  {
    "scheme_name": "Ayushman Bharat",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "income must be <= 500000"
    ]
  },
  {
    "scheme_name": "MGNREGA",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "income must be <= 300000"
    ]
  },
  {
    "scheme_name": "PM-KISAN",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "occupation must be equals farmer"
    ]
  },
  {
    "scheme_name": "Sukanya Samriddhi Yojana",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "age must be <= 10"
    ]
  }
]
```

### Example 5: Farmer with Large Land (Ineligible for PM-KISAN)

This farmer has more than 2 hectares, making them ineligible for PM-KISAN.

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ramesh Yadav",
    "age": 52,
    "income": 350000,
    "state": "Punjab",
    "occupation": "farmer",
    "category": "OBC",
    "land_size": 5.0
  }'
```

**Expected Response (HTTP 200):**
```json
[
  {
    "scheme_name": "Stand Up India",
    "eligible": true,
    "missing_fields": [],
    "failed_conditions": []
  },
  {
    "scheme_name": "Ayushman Bharat",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "income must be <= 500000"
    ]
  },
  {
    "scheme_name": "MGNREGA",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "income must be <= 300000"
    ]
  },
  {
    "scheme_name": "PM-KISAN",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "land_size must be <= 2.0"
    ]
  },
  {
    "scheme_name": "Sukanya Samriddhi Yojana",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "age must be <= 10"
    ]
  }
]
```

### Evaluation with Timing

To measure response time for evaluation:

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": 30,
    "income": 200000,
    "state": "Delhi",
    "occupation": "worker",
    "category": "General",
    "land_size": 0.0
  }' \
  -w "\nTime: %{time_total}s\n"
```

**Expected Output:**
```
[evaluation results...]
Time: 0.450s
```

### Pretty-Printed Response

For better readability, pipe the output through `jq`:

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": 30,
    "income": 200000,
    "state": "Delhi",
    "occupation": "worker",
    "category": "General",
    "land_size": 0.0
  }' | jq .
```

---

## Schemes Endpoint

### Get All Schemes

**Endpoint:** `GET /schemes`

**Purpose:** Retrieve all stored government schemes (useful for debugging)

**Example Request:**
```bash
curl -X GET http://localhost:8000/schemes
```

**Expected Response (HTTP 200):**
```json
[
  {
    "scheme_id": "PM_KISAN",
    "name": "PM-KISAN",
    "description": "Pradhan Mantri Kisan Samman Nidhi - Income support for small and marginal farmer families owning cultivable land up to 2 hectares",
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
  },
  {
    "scheme_id": "AYUSHMAN_BHARAT",
    "name": "Ayushman Bharat",
    "description": "Pradhan Mantri Jan Arogya Yojana - Health insurance scheme for economically vulnerable families with annual income up to 5 lakhs",
    "eligibility_rules": [
      {
        "field": "income",
        "operator": "less_than_or_equal",
        "value": 500000
      }
    ]
  },
  {
    "scheme_id": "SUKANYA_SAMRIDDHI",
    "name": "Sukanya Samriddhi Yojana",
    "description": "Small deposit scheme for the girl child - Savings scheme for parents/guardians of girl children under 10 years of age",
    "eligibility_rules": [
      {
        "field": "age",
        "operator": "less_than_or_equal",
        "value": 10
      }
    ]
  },
  {
    "scheme_id": "MGNREGA",
    "name": "MGNREGA",
    "description": "Mahatma Gandhi National Rural Employment Guarantee Act - Guarantees 100 days of wage employment to rural households with annual income up to 3 lakhs",
    "eligibility_rules": [
      {
        "field": "income",
        "operator": "less_than_or_equal",
        "value": 300000
      }
    ]
  },
  {
    "scheme_id": "STAND_UP_INDIA",
    "name": "Stand Up India",
    "description": "Stand Up India Scheme - Facilitates bank loans for SC/ST entrepreneurs between 18-65 years for setting up greenfield enterprises",
    "eligibility_rules": [
      {
        "field": "age",
        "operator": "greater_than_or_equal",
        "value": 18
      },
      {
        "field": "age",
        "operator": "less_than_or_equal",
        "value": 65
      }
    ]
  }
]
```

### Get Schemes with Pretty Print

```bash
curl -X GET http://localhost:8000/schemes | jq .
```

---

## Performance Expectations

### Response Time Requirements

Based on Requirements 4.5, 5.3:

| Endpoint | Expected Response Time | Requirement |
|----------|----------------------|-------------|
| `/health` | < 100ms | 5.3 |
| `/evaluate` | < 2 seconds | 4.5 |
| `/schemes` | < 500ms | N/A (not specified) |

### Performance Testing Script

Create a simple bash script to test performance:

```bash
#!/bin/bash
# performance_test.sh

echo "Testing /health endpoint performance..."
for i in {1..10}; do
  curl -X GET http://localhost:8000/health \
    -w "Request $i: %{time_total}s\n" \
    -o /dev/null -s
done

echo ""
echo "Testing /evaluate endpoint performance..."
for i in {1..5}; do
  curl -X POST http://localhost:8000/evaluate \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test User",
      "age": 30,
      "income": 200000,
      "state": "Delhi",
      "occupation": "worker",
      "category": "General",
      "land_size": 0.0
    }' \
    -w "Request $i: %{time_total}s\n" \
    -o /dev/null -s
done
```

Make it executable and run:
```bash
chmod +x performance_test.sh
./performance_test.sh
```

---

## Error Scenarios

### Missing Required Fields

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": 30
  }'
```

**Expected Response (HTTP 400):**
```json
{
  "error": "validation_error",
  "message": "Invalid UserProfile data provided",
  "details": [
    {
      "field": "income",
      "error": "Field 'income' is required but missing"
    },
    {
      "field": "state",
      "error": "Field 'state' is required but missing"
    },
    {
      "field": "occupation",
      "error": "Field 'occupation' is required but missing"
    },
    {
      "field": "category",
      "error": "Field 'category' is required but missing"
    },
    {
      "field": "land_size",
      "error": "Field 'land_size' is required but missing"
    }
  ]
}
```

### Invalid Data Types

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": "thirty",
    "income": "high",
    "state": "Delhi",
    "occupation": "worker",
    "category": "General",
    "land_size": "none"
  }'
```

**Expected Response (HTTP 400):**
```json
{
  "error": "validation_error",
  "message": "Invalid UserProfile data provided",
  "details": [
    {
      "field": "age",
      "error": "Field 'age' must be a valid number"
    },
    {
      "field": "income",
      "error": "Field 'income' must be a valid number"
    },
    {
      "field": "land_size",
      "error": "Field 'land_size' must be a valid number"
    }
  ]
}
```

### Out of Range Values

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": 200,
    "income": -5000,
    "state": "Delhi",
    "occupation": "worker",
    "category": "General",
    "land_size": -1.0
  }'
```

**Expected Response (HTTP 400):**
```json
{
  "error": "validation_error",
  "message": "Invalid UserProfile data provided",
  "details": [
    {
      "field": "age",
      "error": "Field 'age' value is out of valid range: Input should be less than or equal to 150"
    },
    {
      "field": "income",
      "error": "Field 'income' value is out of valid range: Input should be greater than or equal to 0"
    },
    {
      "field": "land_size",
      "error": "Field 'land_size' value is out of valid range: Input should be greater than or equal to 0"
    }
  ]
}
```

### Malformed JSON

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": 30,
    "income": 200000
    "state": "Delhi"
  }'
```

**Expected Response (HTTP 400):**
```json
{
  "error": "json_parse_error",
  "message": "Request body contains malformed JSON",
  "details": [
    {
      "field": "body",
      "error": "JSON parsing failed: Expecting ',' delimiter: line 4 column 5 (char 67)"
    }
  ]
}
```

### Empty String Fields

**Request:**
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "",
    "age": 30,
    "income": 200000,
    "state": "",
    "occupation": "worker",
    "category": "General",
    "land_size": 0.0
  }'
```

**Expected Response (HTTP 400):**
```json
{
  "error": "validation_error",
  "message": "Invalid UserProfile data provided",
  "details": [
    {
      "field": "name",
      "error": "Field 'name' cannot be empty"
    },
    {
      "field": "state",
      "error": "Field 'state' cannot be empty"
    }
  ]
}
```

### Invalid Endpoint

**Request:**
```bash
curl -X GET http://localhost:8000/invalid
```

**Expected Response (HTTP 404):**
```json
{
  "detail": "Not Found"
}
```

---

## Testing Checklist

Use this checklist to verify all API functionality:

- [ ] Health check returns 200 with correct structure
- [ ] Health check responds within 100ms
- [ ] Evaluation with valid profile returns 200
- [ ] Evaluation returns all 5 schemes
- [ ] Eligible schemes appear first in results
- [ ] Evaluation responds within 2 seconds
- [ ] Missing fields trigger 400 error
- [ ] Invalid data types trigger 400 error
- [ ] Out of range values trigger 400 error
- [ ] Malformed JSON triggers 400 error
- [ ] Empty strings trigger 400 error
- [ ] Schemes endpoint returns all 5 schemes
- [ ] Invalid endpoints return 404

---

## Additional Resources

- **API Documentation:** Visit `http://localhost:8000/docs` for interactive Swagger UI
- **Alternative API Docs:** Visit `http://localhost:8000/redoc` for ReDoc documentation
- **Root Endpoint:** Visit `http://localhost:8000/` for API information

### Using Swagger UI

The FastAPI automatic documentation provides an interactive interface:

1. Open `http://localhost:8000/docs` in your browser
2. Click on any endpoint to expand it
3. Click "Try it out" button
4. Fill in the request body
5. Click "Execute" to send the request
6. View the response below

This is especially useful for testing without curl commands.

---

## Notes

- All timestamps are in ISO 8601 format with UTC timezone (Z suffix)
- Response times may vary based on system load and network conditions
- The evaluation endpoint is deterministic - same input always produces same output
- All numeric comparisons handle both integers and floats
- Field names and operators are case-sensitive
- State names in eligibility rules are case-insensitive (not implemented in Phase 1)

**Requirements Validated:** 8.3
