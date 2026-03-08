# JanMitra AI Phase 1 Backend

A government scheme eligibility evaluation system built for the AI for Bharat hackathon. This backend provides deterministic rule-based eligibility evaluation for 5 government schemes using FastAPI and DynamoDB.

## Features

- **Deterministic Evaluation**: Pure rule-based eligibility logic without LLM involvement
- **5 Government Schemes**: PM-KISAN, Ayushman Bharat, Sukanya Samriddhi Yojana, MGNREGA, Stand Up India
- **REST API**: FastAPI-based endpoints for health checks, evaluation, and scheme retrieval
- **DynamoDB Storage**: Scalable NoSQL storage for scheme data
- **Explainable Results**: Returns missing fields and failed conditions for each evaluation
- **AWS Ready**: Designed for deployment on AWS EC2 with DynamoDB

## Requirements

- **Python**: 3.9 or higher
- **AWS Account**: For DynamoDB access (or DynamoDB Local for testing)
- **pip**: Python package manager

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd janmitra-ai-phase1-backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# AWS Configuration
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=government_schemes

# API Configuration
API_PORT=8000

# Environment
ENVIRONMENT=development
```

**Note**: For local testing, you can use DynamoDB Local (see below) instead of AWS credentials.

### 5. Set Up DynamoDB

#### Option A: Using DynamoDB Local (Recommended for Testing)

1. Download and install DynamoDB Local:
   ```bash
   # Download DynamoDB Local
   wget https://s3.ap-south-1.amazonaws.com/dynamodb-local-mumbai/dynamodb_local_latest.tar.gz
   
   # Extract
   tar -xzf dynamodb_local_latest.tar.gz
   
   # Run DynamoDB Local
   java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
   ```

2. Update `.env` to use local endpoint:
   ```env
   AWS_REGION=ap-south-1
   DYNAMODB_ENDPOINT_URL=http://localhost:8000
   AWS_ACCESS_KEY_ID=dummy
   AWS_SECRET_ACCESS_KEY=dummy
   ```

3. Create the table:
   ```bash
   aws dynamodb create-table \
     --table-name government_schemes \
     --attribute-definitions AttributeName=scheme_id,AttributeType=S \
     --key-schema AttributeName=scheme_id,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --endpoint-url http://localhost:8000
   ```

#### Option B: Using AWS DynamoDB

1. Ensure you have valid AWS credentials in `.env`

2. Create the table using AWS CLI:
   ```bash
   aws dynamodb create-table \
     --table-name government_schemes \
     --attribute-definitions AttributeName=scheme_id,AttributeType=S \
     --key-schema AttributeName=scheme_id,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --region ap-south-1
   ```

### 6. Seed the Database

Populate the database with the 5 government schemes:

```bash
python -m database.seed_schemes
```

This will load:
- PM-KISAN (for small farmers)
- Ayushman Bharat (health insurance)
- Sukanya Samriddhi Yojana (girl child savings)
- MGNREGA (rural employment)
- Stand Up India (SC/ST entrepreneurs)

To overwrite existing schemes:
```bash
python -m database.seed_schemes --force
```

### 7. Start the Server

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

**Options**:
- `--reload`: Auto-reload on code changes (development mode)
- `--host 0.0.0.0`: Listen on all network interfaces
- `--port 8000`: Specify port (default: 8000)

## API Endpoints

### Health Check

Check if the server is running:

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Evaluate Eligibility

Submit a user profile to evaluate eligibility across all schemes:

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rajesh Kumar",
    "age": 35,
    "income": 250000,
    "state": "Bihar",
    "occupation": "farmer",
    "category": "OBC",
    "land_size": 1.5
  }'
```

**Response**:
```json
[
  {
    "scheme_name": "PM-KISAN",
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
    "scheme_name": "Ayushman Bharat",
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
    "scheme_name": "Sukanya Samriddhi Yojana",
    "eligible": false,
    "missing_fields": [],
    "failed_conditions": [
      "age must be less_than_or_equal to 10 (current: 35)"
    ]
  }
]
```

### Get All Schemes

Retrieve all stored schemes:

```bash
curl http://localhost:8000/schemes
```

**Response**:
```json
[
  {
    "scheme_id": "PM_KISAN",
    "name": "PM-KISAN",
    "description": "Pradhan Mantri Kisan Samman Nidhi - Income support for small and marginal farmer families",
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
]
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_rule_engine.py tests/test_eligibility_service.py

# Integration tests
pytest tests/test_evaluation_integration.py

# Property-based tests
pytest tests/ -k "property"
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

## Project Structure

```
janmitra-ai-phase1-backend/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── README.md                    # This file
│
├── routes/                      # API endpoint definitions
│   ├── health.py               # Health check endpoint
│   ├── evaluation.py           # Eligibility evaluation endpoint
│   └── schemes.py              # Schemes retrieval endpoint
│
├── services/                    # Business logic layer
│   ├── eligibility_service.py  # Evaluation orchestration
│   └── rule_engine.py          # Rule evaluation logic
│
├── models/                      # Data models (Pydantic)
│   ├── user_profile.py         # User profile schema
│   ├── scheme.py               # Scheme and rule schemas
│   └── evaluation_result.py    # Evaluation result schema
│
├── database/                    # Database layer
│   ├── dynamodb_repository.py  # DynamoDB operations
│   └── seed_schemes.py         # Database seeding script
│
├── utils/                       # Utility modules
│   └── logging_config.py       # Structured logging setup
│
└── tests/                       # Test suite
    ├── test_rule_engine.py
    ├── test_eligibility_service.py
    ├── test_evaluation_endpoint.py
    └── ...
```

## Troubleshooting

### DynamoDB Connection Issues

**Error**: `Unable to locate credentials`

**Solution**: Ensure your `.env` file has valid AWS credentials or use DynamoDB Local with dummy credentials.

### Port Already in Use

**Error**: `Address already in use`

**Solution**: Change the port in the uvicorn command:
```bash
uvicorn main:app --reload --port 8001
```

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Seed Script Fails

**Error**: `ResourceNotFoundException: Requested resource not found`

**Solution**: Create the DynamoDB table first (see Step 5 above).

## AWS Deployment

For detailed AWS deployment instructions, see **[docs/AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md)**.

### Quick Overview

The application is designed for deployment on AWS with:
- **EC2 t3.micro** instance running the FastAPI application
- **DynamoDB** table for storing government schemes
- **IAM role-based authentication** (no hardcoded credentials)
- **Security group** allowing HTTP traffic on port 8000
- **Systemd service** for automatic startup and restart

Key deployment steps:
1. Create IAM role with DynamoDB permissions
2. Create DynamoDB table (`government_schemes`)
3. Launch EC2 instance with IAM role attached
4. Configure security group (ports 22, 8000)
5. Install application and dependencies
6. Seed database with 5 government schemes
7. Set up systemd service for auto-start

For complete step-by-step instructions, troubleshooting, and production best practices, refer to the [AWS Deployment Guide](docs/AWS_DEPLOYMENT.md).

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

For comprehensive API testing examples with curl commands, see **[docs/API_TESTING.md](docs/API_TESTING.md)**.

## License

This project is built for the AI for Bharat hackathon.

## Support

For issues or questions, please contact the development team.
