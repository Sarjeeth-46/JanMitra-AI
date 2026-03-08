"""
Unit tests for health check endpoint

Tests the /health endpoint to ensure it returns correct status,
timestamp format, and response time requirements.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import time
from main import app

client = TestClient(app)


def test_health_check_returns_200():
    """Test that health check returns HTTP 200 status"""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_structure():
    """Test that health check returns correct JSON structure"""
    response = client.get("/health")
    data = response.json()
    
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"


def test_health_check_timestamp_format():
    """Test that timestamp is in valid ISO 8601 format"""
    response = client.get("/health")
    data = response.json()
    
    timestamp = data["timestamp"]
    
    # Verify it ends with 'Z' (UTC indicator)
    assert timestamp.endswith("Z")
    
    # Verify it can be parsed as ISO 8601
    # Remove 'Z' and parse
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    assert isinstance(parsed, datetime)


def test_health_check_response_time():
    """Test that health check responds within 100ms"""
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()
    
    response_time_ms = (end_time - start_time) * 1000
    
    assert response.status_code == 200
    assert response_time_ms < 100, f"Response time {response_time_ms}ms exceeds 100ms requirement"


def test_health_check_timestamp_is_recent():
    """Test that timestamp is current (within last second)"""
    response = client.get("/health")
    data = response.json()
    
    timestamp_str = data["timestamp"]
    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    now = datetime.now(timestamp.tzinfo)
    
    # Timestamp should be within 1 second of current time
    time_diff = abs((now - timestamp).total_seconds())
    assert time_diff < 1.0, f"Timestamp is {time_diff}s old, should be current"
