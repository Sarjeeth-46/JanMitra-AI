"""
Unit tests for the eligibility evaluation service.

Tests the orchestration of scheme evaluation across all government schemes.
"""

import pytest
from unittest.mock import AsyncMock, patch
from models.user_profile import UserProfile
from models.scheme import Scheme, EligibilityRule
from models.evaluation_result import EvaluationResult
from services.eligibility_service import evaluate_eligibility


@pytest.mark.asyncio
async def test_evaluate_eligibility_with_multiple_schemes():
    """Test that evaluate_eligibility processes all schemes and returns results."""
    # Create a test user profile
    user_profile = UserProfile(
        name="Test User",
        age=30,
        income=200000,
        state="Karnataka",
        occupation="farmer",
        category="General",
        land_size=1.5
    )
    
    # Create mock schemes
    mock_schemes = [
        Scheme(
            scheme_id="TEST_SCHEME_1",
            name="Test Scheme 1",
            description="First test scheme",
            eligibility_rules=[
                EligibilityRule(field="occupation", operator="equals", value="farmer")
            ]
        ),
        Scheme(
            scheme_id="TEST_SCHEME_2",
            name="Test Scheme 2",
            description="Second test scheme",
            eligibility_rules=[
                EligibilityRule(field="age", operator="greater_than_or_equal", value=18)
            ]
        )
    ]
    
    # Mock the DynamoDB repository
    with patch('database.dynamodb_repository.DynamoDBRepository.get_all_schemes', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_schemes
        
        # Call the function
        results = await evaluate_eligibility(user_profile)
        
        # Verify results
        assert len(results) == 2
        assert all(isinstance(r, EvaluationResult) for r in results)
        assert results[0].scheme_name == "Test Scheme 1"
        assert results[1].scheme_name == "Test Scheme 2"
        
        # Verify both schemes are eligible for this profile
        assert results[0].eligible == True
        assert results[1].eligible == True


@pytest.mark.asyncio
async def test_evaluate_eligibility_with_empty_schemes():
    """Test that evaluate_eligibility handles empty scheme list gracefully."""
    user_profile = UserProfile(
        name="Test User",
        age=30,
        income=200000,
        state="Karnataka",
        occupation="farmer",
        category="General",
        land_size=1.5
    )
    
    # Mock the DynamoDB repository to return empty list
    with patch('database.dynamodb_repository.DynamoDBRepository.get_all_schemes', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        
        # Call the function
        results = await evaluate_eligibility(user_profile)
        
        # Verify results
        assert len(results) == 0


@pytest.mark.asyncio
async def test_evaluate_eligibility_with_ineligible_schemes():
    """Test that evaluate_eligibility correctly identifies ineligible schemes."""
    user_profile = UserProfile(
        name="Test User",
        age=18,  # Age 18 passes pydantic but fails the rule logic test
        income=200000,
        state="Karnataka",
        occupation="student",
        category="General",
        land_size=0
    )
    
    # Create mock scheme with age requirement
    mock_schemes = [
        Scheme(
            scheme_id="TEST_SCHEME",
            name="Test Scheme",
            description="Test scheme with age requirement",
            eligibility_rules=[
                EligibilityRule(field="age", operator="greater_than_or_equal", value=21)
            ]
        )
    ]
    
    # Mock the DynamoDB repository
    with patch('database.dynamodb_repository.DynamoDBRepository.get_all_schemes', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_schemes
        
        # Call the function
        results = await evaluate_eligibility(user_profile)
        
        # Verify results
        assert len(results) == 1
        assert results[0].eligible == False
        assert len(results[0].failed_conditions) > 0
