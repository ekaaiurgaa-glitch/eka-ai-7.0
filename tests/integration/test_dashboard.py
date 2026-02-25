import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_workshop_dashboard(client: AsyncClient, auth_headers: dict, db_session):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="DASH1", make="Maruti", model="Swift", year=2019, fuel_type=v_schema.FuelType.petrol),
        "test_tenant",
    )
    await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Service"),
        "test_tenant",
        "test_user",
    )

    response = await client.get("/api/v1/dashboard/workshop", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "daily_revenue" in data
    assert "jobs_by_status" in data


@pytest.mark.asyncio
async def test_fleet_dashboard(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/dashboard/fleet", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "cost_per_vehicle" in data


@pytest.mark.asyncio
async def test_owner_dashboard_with_vehicle_id(client: AsyncClient, auth_headers: dict, db_session):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="OWNER1", make="Honda", model="City", year=2020, fuel_type=v_schema.FuelType.diesel),
        "test_tenant",
    )
    await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Maintenance"),
        "test_tenant",
        "test_user",
    )

    response = await client.get(
        f"/api/v1/dashboard/owner?vehicle_id={vehicle.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_spend_ytd" in data
    assert "service_history" in data

@pytest.mark.asyncio
async def test_owner_dashboard_without_vehicle_id(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/dashboard/owner", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_dashboard_type(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/dashboard/invalid_type", headers=auth_headers)
    assert response.status_code == 404
