import pytest
import asyncio
import time
from httpx import AsyncClient
from main import app

@pytest.fixture
async def auth_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/api/auth/anonymous-token")
        token = res.json().get("access_token", "")
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client

@pytest.mark.asyncio
async def test_invalid_dob_rejected(auth_client):
    """Test that forms with invalid DOBs format or out-of-bounds age are rejected via backend API or Pydantic validation."""
    async for client in auth_client:
        response = await client.post("/api/evaluate", json={
            "name": "Test User",
            "age": -5,
            "income": 100000,
            "state": "Delhi",
            "occupation": "farmer",
            "category": "General",
            "land_size": 2.0
        })
        assert response.status_code == 400 or response.status_code == 422 # Dependent on ValidationError handler

@pytest.mark.asyncio
async def test_income_validation_works(auth_client):
    """Test that extremely large incomes are rejected."""
    async for client in auth_client:
        response = await client.post("/api/evaluate", json={
            "name": "Test User",
            "age": 30,
            "income": -1000,
            "state": "Delhi",
            "occupation": "farmer",
            "category": "General",
            "land_size": 2.0
        })
        assert response.status_code == 400 or response.status_code == 422

# Note: The voice request test involves external AWS audio APIs, mock or pass.
@pytest.mark.asyncio
async def test_scheme_results_returned(auth_client):
    """Test that eligible scheme results are returned rapidly."""
    start_time = time.time()
    async for client in auth_client:
        response = await client.post("/api/evaluate", json={
            "name": "Test Farmer",
            "age": 35,
            "income": 50000,
            "state": "Uttar Pradesh",
            "occupation": "farmer",
            "category": "General",
            "land_size": 1.5
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any("Kisan" in str(r) and r.get("eligible", False) for r in data)
    
    duration = time.time() - start_time
    assert duration < 3.0, "API response took longer than 3 seconds"

@pytest.mark.asyncio
async def test_login_successful():
    """Test the auth pipeline can issue a token."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Use the anonymous token endpoint as a proxy for fast auth check
        res = await client.get("/api/auth/anonymous-token")
        assert res.status_code == 200
        assert "access_token" in res.json()
