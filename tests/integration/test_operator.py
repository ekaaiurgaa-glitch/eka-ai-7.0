import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_operator_execute_generates_preview(client: AsyncClient, auth_headers: dict, db_session):
    from app.modules.vehicles import service, schema

    vehicle = await service.create_vehicle(
        db_session,
        schema.VehicleCreate(plate_number="OP123", make="Maruti", model="Swift", year=2019, fuel_type=schema.FuelType.petrol),
        "test_tenant",
    )

    response = await client.post(
        "/api/v1/operator/execute",
        json={
            "intent": "create_job_card",
            "args": {"vehicle_id": vehicle.id, "complaint": "Brake issue"},
            "tenant_id": "test_tenant",
            "actor_id": "test_user",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "preview_id" in data
    assert "action_preview" in data


@pytest.mark.asyncio
async def test_operator_confirm_success(client: AsyncClient, auth_headers: dict, db_session):
    from app.modules.vehicles import service, schema
    from app.modules.operator import tool_handler, schema as op_schema

    vehicle = await service.create_vehicle(
        db_session,
        schema.VehicleCreate(plate_number="OP456", make="Honda", model="City", year=2020, fuel_type=schema.FuelType.diesel),
        "test_tenant",
    )

    preview = await tool_handler.generate_preview(
        db_session,
        op_schema.OperatorExecuteRequest(
            intent="create_job_card",
            args={"vehicle_id": vehicle.id, "complaint": "Service"},
            tenant_id="test_tenant",
            actor_id="test_user",
        ),
    )

    response = await client.post(
        "/api/v1/operator/confirm",
        json={"preview_id": preview.preview_id, "confirm": True, "actor_id": "test_user"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "cancelled"]


@pytest.mark.asyncio
async def test_operator_confirm_wrong_preview_id(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/operator/confirm",
        json={"preview_id": "invalid-preview-id", "confirm": True, "actor_id": "test_user"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_operator_confirm_expired_preview(client: AsyncClient, auth_headers: dict, db_session):
    from app.modules.operator import model
    from datetime import datetime, timezone, timedelta

    expired_preview = model.OperatorPreview(
        id="expired-123",
        tenant_id="test_tenant",
        actor_id="test_user",
        tool_name="create_job_card",
        args_json={"vehicle_id": 1, "complaint": "Test"},
        preview_json={"action": "create_job_card"},
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    db_session.add(expired_preview)
    await db_session.commit()

    response = await client.post(
        "/api/v1/operator/confirm",
        json={"preview_id": "expired-123", "confirm": True, "actor_id": "test_user"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()
