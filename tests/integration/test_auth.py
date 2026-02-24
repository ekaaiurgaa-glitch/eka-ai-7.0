import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post("/token", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post("/token", data={"username": "admin", "password": "wrong"})
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_wrong_username(client: AsyncClient):
    response = await client.post("/token", data={"username": "hacker", "password": "admin"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    response = await client.get("/api/v1/vehicles")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/v1/vehicles",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/vehicles", headers=auth_headers)
    assert response.status_code == 200
