"""
Integration tests for evaluation endpoint with eligibility service

Tests the complete evaluation flow from endpoint through service layer
to rule engine, using mocked DynamoDB data.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from models.scheme import Scheme, EligibilityRule
from middleware.auth import verify_token

# Mock authentication
async def override_verify_token():
    return {"sub": "1234567890", "phone": "+919876543210"}
app.dependency_overrides[verify_token] = override_verify_token

client = TestClient(app)


@pytest.fixture
def mock_schemes():
    """Fixture providing mock schemes from DynamoDB"""
    return [
        Scheme(
            scheme_id="PM_KISAN",
            name="PM-KISAN",
            description="Income support for farmers",
            eligibility_rules=[
                EligibilityRule(field="occupation", operator="equals", value="farmer"),
                EligibilityRule(field="land_size", operator="less_than_or_equal", value=2.0)
            ]
        ),
        Scheme(
            scheme_id="AYUSHMAN_BHARAT",
            name="Ayushman Bharat",
            description="Health insurance scheme",
            eligibility_rules=[
                EligibilityRule(field="income", operator="less_than_or_equal", value=500000)
            ]
        ),
        Scheme(
            scheme_id="MGNREGA",
            name="MGNREGA",
            description="Rural employment guarantee",
            eligibility_rules=[
                EligibilityRule(field="income", operator="less_than_or_equal", value=300000)
            ]
        )
    ]


def test_integration_eligible_farmer_profile(mock_schemes):
    """Test complete flow with a farmer profile eligible for PM-KISAN"""
    farmer_profile = {
        "name": "Rajesh Kumar",
        "age": 35,
        "income": 250000,
        "state": "Maharashtra",
        "occupation": "farmer",
        "category": "OBC",
        "land_size": 1.5
    }
    
    with patch('database.dynamodb_repository.DynamoDBRepository.get_all_schemes', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_schemes
        
        response = client.post("/evaluate", json=farmer_profile)
        
        assert response.status_code == 200
        results = response.json()
        
        # Should return results for all 3 schemes
        assert len(results) == 3
        
        # Find PM-KISAN result
        pm_kisan_result = next((r for r in results if r["scheme_name"] == "PM-KISAN"), None)
        assert pm_kisan_result is not None
        assert pm_kisan_result["eligible"] is True
        assert len(pm_kisan_result["missing_fields"]) == 0
        assert len(pm_kisan_result["failed_conditions"]) == 0


def test_integration_low_income_profile(mock_schemes):
    """Test complete flow with a low-income profile eligible for MGNREGA"""
    low_income_profile = {
        "name": "Priya Sharma",
        "age": 28,
        "income": 200000,
        "state": "Bihar",
        "occupation": "laborer",
        "category": "SC",
        "land_size": 0.0
    }
    
    with patch('database.dynamodb_repository.DynamoDBRepository.get_all_schemes', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_schemes
        
        response = client.post("/evaluate", json=low_income_profile)
        
        assert response.status_code == 200
        results = response.json()
        
        # Find MGNREGA result
        mgnrega_result = next((r for r in results if r["scheme_name"] == "MGNREGA"), None)
        assert mgnrega_result is not None
        assert mgnrega_result["eligible"] is True
        
        # Should also be eligible for Ayushman Bharat (income <= 500000)
        ayushman_result = next((r for r in results if r["scheme_name"] == "Ayushman Bharat"), None)
        assert ayushman_result is not None
        assert ayushman_result["eligible"] is True


def test_integration_high_income_profile(mock_schemes):
    """Test complete flow with a high-income profile ineligible for income-based schemes"""
    high_income_profile = {
        "name": "Amit Patel",
        "age": 45,
        "income": 800000,
        "state": "Gujarat",
        "occupation": "business",
        "category": "General",
        "land_size": 0.0
    }
    
    with patch('database.dynamodb_repository.DynamoDBRepository.get_all_schemes', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_schemes
        
        response = client.post("/evaluate", json=high_income_profile)
        
        assert response.status_code == 200
        results = response.json()
        
        # Should be ineligible for income-based schemes
        ayushman_result = next((r for r in results if r["scheme_name"] == "Ayushman Bharat"), None)
        assert ayushman_result is not None
        assert ayushman_result["eligible"] is False
        assert "income" in ayushman_result["failed_conditions"][0].lower()
        
        mgnrega_result = next((r for r in results if r["scheme_name"] == "MGNREGA"), None)
        assert mgnrega_result is not None
        assert mgnrega_result["eligible"] is False


def test_integration_ranking_eligible_first(mock_schemes):
    """Test that eligible schemes are ranked before ineligible ones"""
    mixed_profile = {
        "name": "Test User",
        "age": 30,
        "income": 250000,  # Eligible for both Ayushman and MGNREGA
        "state": "Karnataka",
        "occupation": "teacher",  # Not a farmer
        "category": "OBC",
        "land_size": 0.5
    }
    
    with patch('database.dynamodb_repository.DynamoDBRepository.get_all_schemes', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_schemes
        
        response = client.post("/evaluate", json=mixed_profile)
        
        assert response.status_code == 200
        results = response.json()
        
        # Find first ineligible scheme index
        first_ineligible_idx = next(
            (i for i, r in enumerate(results) if not r["eligible"]),
            len(results)
        )
        
        # All schemes before first_ineligible_idx should be eligible
        for i in range(first_ineligible_idx):
            assert results[i]["eligible"] is True, f"Scheme at index {i} should be eligible"
        
        # All schemes after should be ineligible
        for i in range(first_ineligible_idx, len(results)):
            assert results[i]["eligible"] is False, f"Scheme at index {i} should be ineligible"


def test_integration_response_time(mock_schemes):
    """Test that evaluation completes within reasonable time"""
    import time
    
    profile = {
        "name": "Test User",
        "age": 30,
        "income": 250000,
        "state": "Karnataka",
        "occupation": "farmer",
        "category": "OBC",
        "land_size": 1.0
    }
    
    with patch('database.dynamodb_repository.DynamoDBRepository.get_all_schemes', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_schemes
        
        start_time = time.time()
        response = client.post("/evaluate", json=profile)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Should complete within reasonable time (requirement 4.5 specifies 2s for production)
        # Allow some overhead for test environment
        assert response_time < 3.0, f"Response time {response_time}s is too slow"
