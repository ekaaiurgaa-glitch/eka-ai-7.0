import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_job_card(client: AsyncClient, auth_headers: dict, db_session, test_tenant):
    # First create a vehicle
    from app.modules.vehicles import service, schema
    vehicle = await service.create_vehicle(
        db_session,
        schema.VehicleCreate(plate_number="TEST123", make="Maruti", model="Swift", variant="VXI", year=2019, fuel_type=schema.FuelType.petrol),
        test_tenant,
    )

    response = await client.post(
        "/api/v1/job-cards",
        json={"vehicle_id": vehicle.id, "complaint": "Brake noise", "state": "OPEN"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["job_no"].startswith("JB-")
    assert data["complaint"] == "Brake noise"


@pytest.mark.asyncio
async def test_get_job_card(client: AsyncClient, auth_headers: dict, db_session, test_tenant):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="GET123", make="Honda", model="City", variant="VX", year=2020, fuel_type=v_schema.FuelType.diesel),
        "test_tenant",
    )
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Engine issue"),
        "test_tenant",
        "test_user",
    )

    response = await client.get(f"/api/v1/job-cards/{job.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == job.id


@pytest.mark.asyncio
async def test_transition_job_card_state(client: AsyncClient, auth_headers: dict, db_session, test_tenant):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="TR123", make="Tata", model="Nexon", variant="EV", year=2021, fuel_type=v_schema.FuelType.electric),
        "test_tenant",
    )
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Battery check"),
        test_tenant,
        "test_user",
    )

    response = await client.patch(
        f"/api/v1/job-cards/{job.id}/transition",
        json={"new_state": "DIAGNOSIS"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["state"] == "DIAGNOSIS"


@pytest.mark.asyncio
async def test_invalid_state_transition(client: AsyncClient, auth_headers: dict, db_session, test_tenant):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="INV123", make="Maruti", model="Alto", variant="LXI", year=2018, fuel_type=v_schema.FuelType.petrol),
        test_tenant,
    )
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Test"),
        test_tenant,
        "test_user",
    )

    response = await client.patch(
        f"/api/v1/job-cards/{job.id}/transition",
        json={"new_state": "CLOSED"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "Invalid state transition" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_estimate(client: AsyncClient, auth_headers: dict, db_session, test_tenant):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="EST123", make="Hyundai", model="i20", variant="Sportz", year=2020, fuel_type=v_schema.FuelType.petrol),
        test_tenant,
    )
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Service"),
        test_tenant,
        "test_user",
    )
    await j_service.transition_job_card_state(db_session, job.id, "DIAGNOSIS", "test_tenant", "test_user")

    response = await client.post(
        f"/api/v1/job-cards/{job.id}/estimate",
        json={
            "lines": [
                {"description": "Oil Filter", "quantity": 1, "price": 200.0},
                {"description": "Engine Oil", "quantity": 4, "price": 150.0},
            ]
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_parts"] > 0

@pytest.mark.asyncio
async def test_high_value_estimate_approval(client: AsyncClient, auth_headers: dict, db_session, test_tenant):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="HIGH123", make="BMW", model="X5", variant="M", year=2023, fuel_type=v_schema.FuelType.diesel),
        test_tenant,
    )
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Major service"),
        test_tenant,
        "test_user",
    )
    await j_service.transition_job_card_state(db_session, job.id, "DIAGNOSIS", "test_tenant", "test_user")

    # High value estimate (> 10,000)
    response = await client.post(
        f"/api/v1/job-cards/{job.id}/estimate",
        json={
            "lines": [
                {"description": "Major Parts", "quantity": 1, "price": 15000.0},
            ],
            "total_labor": 5000.0
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    
    # Check if job transitioned to APPROVAL_PENDING
    job_res = await client.get(f"/api/v1/job-cards/{job.id}", headers=auth_headers)
    assert job_res.json()["state"] == "APPROVAL_PENDING"

