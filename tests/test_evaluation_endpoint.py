"""
Unit tests for evaluation endpoint

Tests the POST /evaluate endpoint to ensure it accepts UserProfile data,
returns ranked evaluation results, and handles errors appropriately.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from models.evaluation_result import EvaluationResult
from middleware.auth import verify_token

# Mock authentication
async def override_verify_token():
    return {"sub": "1234567890", "phone": "+919876543210"}
app.dependency_overrides[verify_token] = override_verify_token

client = TestClient(app)


@pytest.fixture
def valid_user_profile():
    """Fixture providing a valid user profile"""
    return {
        "name": "Rajesh Kumar",
        "age": 35,
        "income": 250000,
        "state": "Maharashtra",
        "occupation": "farmer",
        "category": "OBC",
        "land_size": 1.5
    }


@pytest.fixture
def mock_evaluation_results():
    """Fixture providing mock evaluation results"""
    return [
        EvaluationResult(
            scheme_name="PM-KISAN",
            eligible=True,
            missing_fields=[],
            failed_conditions=[]
        ),
        EvaluationResult(
            scheme_name="Ayushman Bharat",
            eligible=False,
            missing_fields=[],
            failed_conditions=["income must be <= 500000"]
        )
    ]


def test_evaluate_endpoint_returns_200_with_valid_profile(valid_user_profile, mock_evaluation_results):
    """Test that /evaluate returns HTTP 200 with valid UserProfile"""
    with patch('routes.evaluation.evaluate_eligibility', new_callable=AsyncMock) as mock_eval:
        mock_eval.return_value = mock_evaluation_results
        
        response = client.post("/evaluate", json=valid_user_profile)
        
        assert response.status_code == 200
        mock_eval.assert_called_once()


def test_evaluate_endpoint_response_structure(valid_user_profile, mock_evaluation_results):
    """Test that /evaluate returns correct JSON array structure"""
    with patch('routes.evaluation.evaluate_eligibility', new_callable=AsyncMock) as mock_eval:
        mock_eval.return_value = mock_evaluation_results
        
        response = client.post("/evaluate", json=valid_user_profile)
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check first result structure
        result = data[0]
        assert "scheme_name" in result
        assert "eligible" in result
        assert "missing_fields" in result
        assert "failed_conditions" in result
        assert isinstance(result["eligible"], bool)
        assert isinstance(result["missing_fields"], list)
        assert isinstance(result["failed_conditions"], list)


def test_evaluate_endpoint_returns_400_with_missing_fields():
    """Test that /evaluate returns HTTP 400 when required fields are missing"""
    invalid_profile = {
        "name": "Test User",
        "age": 30
        # Missing: income, state, occupation, category, land_size
    }
    
    response = client.post("/evaluate", json=invalid_profile)
    
    assert response.status_code == 400  # Custom handler returns 400 for validation errors
    data = response.json()
    assert data["error"] == "validation_error"
    assert "message" in data
    assert "details" in data
    assert isinstance(data["details"], list)


def test_evaluate_endpoint_returns_400_with_invalid_age():
    """Test that /evaluate returns HTTP 400 with invalid age value"""
    invalid_profile = {
        "name": "Test User",
        "age": 200,  # Invalid: exceeds 150
        "income": 100000,
        "state": "Maharashtra",
        "occupation": "farmer",
        "category": "General",
        "land_size": 1.0
    }
    
    response = client.post("/evaluate", json=invalid_profile)
    
    assert response.status_code == 400  # Custom handler returns 400
    data = response.json()
    assert data["error"] == "validation_error"


def test_evaluate_endpoint_returns_400_with_negative_income():
    """Test that /evaluate returns HTTP 400 with negative income"""
    invalid_profile = {
        "name": "Test User",
        "age": 30,
        "income": -50000,  # Invalid: negative
        "state": "Maharashtra",
        "occupation": "farmer",
        "category": "General",
        "land_size": 1.0
    }
    
    response = client.post("/evaluate", json=invalid_profile)
    
    assert response.status_code == 400  # Custom handler returns 400
    data = response.json()
    assert data["error"] == "validation_error"


def test_evaluate_endpoint_returns_400_with_empty_name():
    """Test that /evaluate returns HTTP 400 with empty name"""
    invalid_profile = {
        "name": "",  # Invalid: empty string
        "age": 30,
        "income": 100000,
        "state": "Maharashtra",
        "occupation": "farmer",
        "category": "General",
        "land_size": 1.0
    }
    
    response = client.post("/evaluate", json=invalid_profile)
    
    assert response.status_code == 400  # Custom handler returns 400
    data = response.json()
    assert data["error"] == "validation_error"


def test_evaluate_endpoint_returns_400_with_malformed_json():
    """Test that /evaluate returns HTTP 400 with malformed JSON"""
    response = client.post(
        "/evaluate",
        data="{ invalid json }",
        headers={"Content-Type": "application/json"}
    )
    
    # Malformed JSON should return 400 with json_parse_error or validation_error
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"] in ["json_parse_error", "validation_error"]


def test_evaluate_endpoint_calls_eligibility_service(valid_user_profile, mock_evaluation_results):
    """Test that /evaluate calls the eligibility service with correct profile"""
    with patch('routes.evaluation.evaluate_eligibility', new_callable=AsyncMock) as mock_eval:
        mock_eval.return_value = mock_evaluation_results
        
        response = client.post("/evaluate", json=valid_user_profile)
        
        assert response.status_code == 200
        mock_eval.assert_called_once()
        
        # Verify the UserProfile was passed correctly
        call_args = mock_eval.call_args[0][0]
        assert call_args.name == valid_user_profile["name"]
        assert call_args.age == valid_user_profile["age"]
        assert call_args.income == valid_user_profile["income"]


def test_evaluate_endpoint_handles_service_errors(valid_user_profile):
    """Test that /evaluate returns HTTP 500 when service raises exception"""
    with patch('routes.evaluation.evaluate_eligibility', new_callable=AsyncMock) as mock_eval:
        mock_eval.side_effect = Exception("Database connection failed")
        
        response = client.post("/evaluate", json=valid_user_profile)
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()



def test_evaluate_endpoint_returns_400_with_invalid_data_types():
    """Test that /evaluate returns HTTP 400 with invalid data types"""
    invalid_profile = {
        "name": "Test User",
        "age": "thirty",  # Invalid: should be integer
        "income": 100000,
        "state": "Maharashtra",
        "occupation": "farmer",
        "category": "General",
        "land_size": 1.0
    }
    
    response = client.post("/evaluate", json=invalid_profile)
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "validation_error"
    assert "details" in data
    # Check that the error mentions the age field
    assert any("age" in detail["field"] for detail in data["details"])


def test_evaluate_endpoint_error_response_structure():
    """Test that error responses have consistent structure"""
    invalid_profile = {
        "name": "Test User"
        # Missing all other required fields
    }
    
    response = client.post("/evaluate", json=invalid_profile)
    
    assert response.status_code == 400
    data = response.json()
    
    # Verify error response structure
    assert "error" in data
    assert "message" in data
    assert "details" in data
    assert isinstance(data["details"], list)
    
    # Each detail should have field and error
    for detail in data["details"]:
        assert "field" in detail
        assert "error" in detail


def test_evaluate_endpoint_returns_400_with_wrong_type_for_numeric_fields():
    """Test that /evaluate returns HTTP 400 when numeric fields have wrong types"""
    invalid_profile = {
        "name": "Test User",
        "age": 30,
        "income": "not_a_number",  # Invalid: should be float
        "state": "Maharashtra",
        "occupation": "farmer",
        "category": "General",
        "land_size": 1.0
    }
    
    response = client.post("/evaluate", json=invalid_profile)
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "validation_error"
    assert any("income" in detail["field"] for detail in data["details"])
