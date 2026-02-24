import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mg_calculate_known_vehicle(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/mg/calculate",
        json={
            "make": "Maruti",
            "model": "Swift",
            "year": 2019,
            "fuel_type": "petrol",
            "city": "Mumbai",
            "monthly_km": 1000,
            "warranty_status": "out_of_warranty",
            "usage_type": "personal",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "monthly_mg" in data
    assert data["monthly_mg"] > 0


@pytest.mark.asyncio
async def test_mg_calculate_unknown_vehicle_uses_default(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/mg/calculate",
        json={
            "make": "UnknownMake",
            "model": "UnknownModel",
            "year": 2020,
            "fuel_type": "electric",
            "city": "Delhi",
            "monthly_km": 1500,
            "warranty_status": "out_of_warranty",
            "usage_type": "commercial",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "monthly_mg" in data


@pytest.mark.asyncio
async def test_mg_calculate_with_warranty(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/mg/calculate",
        json={
            "make": "Maruti",
            "model": "Swift",
            "year": 2023,
            "fuel_type": "petrol",
            "city": "Bangalore",
            "monthly_km": 800,
            "warranty_status": "under_warranty",
            "usage_type": "personal",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_mg"] >= 0
