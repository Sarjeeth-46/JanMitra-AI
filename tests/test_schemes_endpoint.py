"""
Unit tests for the schemes endpoint.

Tests the GET /schemes endpoint that retrieves all stored government schemes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from models.scheme import Scheme, EligibilityRule

client = TestClient(app)


@patch('routes.schemes.DynamoDBRepository')
def test_get_schemes_success(mock_repository_class):
    """Test that GET /schemes returns all schemes successfully."""
    
    # Arrange - Create mock schemes
    mock_schemes = [
        Scheme(
            scheme_id="PM_KISAN",
            name="PM-KISAN",
            description="Income support for farmer families",
            eligibility_rules=[
                EligibilityRule(field="occupation", operator="equals", value="farmer"),
                EligibilityRule(field="land_size", operator="less_than_or_equal", value=2.0)
            ]
        ),
        Scheme(
            scheme_id="AYUSHMAN_BHARAT",
            name="Ayushman Bharat",
            description="Health insurance for low-income families",
            eligibility_rules=[
                EligibilityRule(field="income", operator="less_than_or_equal", value=500000),
                EligibilityRule(field="category", operator="equals", value="SC")
            ]
        )
    ]
    
    # Mock the repository instance and its method
    mock_repository = mock_repository_class.return_value
    mock_repository.get_all_schemes = AsyncMock(return_value=mock_schemes)
    
    # Act
    response = client.get("/schemes")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["scheme_id"] == "PM_KISAN"
    assert data[0]["name"] == "PM-KISAN"
    assert data[1]["scheme_id"] == "AYUSHMAN_BHARAT"
    assert data[1]["name"] == "Ayushman Bharat"


@patch('routes.schemes.DynamoDBRepository')
def test_get_schemes_empty_database(mock_repository_class):
    """Test that GET /schemes handles empty database gracefully."""
    
    # Arrange - Mock empty schemes list
    mock_repository = mock_repository_class.return_value
    mock_repository.get_all_schemes = AsyncMock(return_value=[])
    
    # Act
    response = client.get("/schemes")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == []


@patch('routes.schemes.DynamoDBRepository')
def test_get_schemes_database_error(mock_repository_class):
    """Test that GET /schemes handles database errors appropriately."""
    
    # Arrange - Mock database error
    mock_repository = mock_repository_class.return_value
    mock_repository.get_all_schemes = AsyncMock(side_effect=Exception("DynamoDB connection failed"))
    
    # Act
    response = client.get("/schemes")
    
    # Assert
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "DynamoDB connection failed" in data["detail"]


@patch('routes.schemes.DynamoDBRepository')
def test_get_schemes_returns_complete_scheme_data(mock_repository_class):
    """Test that GET /schemes returns complete scheme data including all fields."""
    
    # Arrange - Create a scheme with multiple rules
    mock_scheme = Scheme(
        scheme_id="TEST_SCHEME",
        name="Test Scheme",
        description="A test scheme for verification",
        eligibility_rules=[
            EligibilityRule(field="age", operator="greater_than_or_equal", value=18),
            EligibilityRule(field="age", operator="less_than_or_equal", value=65),
            EligibilityRule(field="income", operator="less_than", value=300000)
        ]
    )
    
    mock_repository = mock_repository_class.return_value
    mock_repository.get_all_schemes = AsyncMock(return_value=[mock_scheme])
    
    # Act
    response = client.get("/schemes")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    
    scheme = data[0]
    assert scheme["scheme_id"] == "TEST_SCHEME"
    assert scheme["name"] == "Test Scheme"
    assert scheme["description"] == "A test scheme for verification"
    assert len(scheme["eligibility_rules"]) == 3
    
    # Verify first rule
    assert scheme["eligibility_rules"][0]["field"] == "age"
    assert scheme["eligibility_rules"][0]["operator"] == "greater_than_or_equal"
    assert scheme["eligibility_rules"][0]["value"] == 18
