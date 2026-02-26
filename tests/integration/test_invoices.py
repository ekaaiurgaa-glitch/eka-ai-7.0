import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_invoice(client: AsyncClient, auth_headers: dict, db_session):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="INV001", make="Maruti", model="Swift", variant="VXI", year=2019, fuel_type=v_schema.FuelType.petrol),
        "test_tenant",
    )
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Service"),
        "test_tenant",
        "test_user",
    )

    response = await client.post(
        "/api/v1/invoices",
        json={
            "job_id": job.id,
            "lines": [
                {"part_id": 1, "quantity": 1, "price": 100.0, "tax_rate": 0.18, "hsn_code": "8708"},
                {"part_id": 2, "quantity": 2, "price": 50.0, "tax_rate": 0.18, "hsn_code": "2710"},
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["job_id"] == job.id


@pytest.mark.asyncio
async def test_get_invoice(client: AsyncClient, auth_headers: dict, db_session):
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema
    from app.modules.invoices import service as i_service, schema as i_schema

    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="INV002", make="Honda", model="City", variant="VX", year=2020, fuel_type=v_schema.FuelType.diesel),
        "test_tenant",
    )
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Repair"),
        "test_tenant",
        "test_user",
    )
    invoice = await i_service.create_invoice(
        db_session,
        i_schema.InvoiceCreate(
            job_id=job.id,
            lines=[
                {"part_id": 1, "quantity": 1, "price": 100.0, "tax_rate": 0.18, "hsn_code": "8708"},
            ],
        ),
        "test_tenant",
    )

    response = await client.get(f"/api/v1/invoices/{invoice.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == invoice.id


@pytest.mark.asyncio
async def test_get_nonexistent_invoice(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/invoices/99999", headers=auth_headers)
    assert response.status_code == 404
