import pytest
from app.modules.catalog import service, schema, model


@pytest.mark.asyncio
async def test_create_and_get_part(db_session):
    part_data = schema.PartCreate(
        part_number="BRK-001",
        description="Brake Pad Set",
        hsn_code="8708",
        unit_price=1500.0,
        gst_rate=18.0,
    )
    part = await service.create_part(db_session, part_data, "test_tenant")
    assert part.id is not None
    assert part.part_number == "BRK-001"

    retrieved = await service.get_part(db_session, part.id, "test_tenant")
    assert retrieved.part_number == "BRK-001"


@pytest.mark.asyncio
async def test_get_nonexistent_part_raises_404(db_session):
    with pytest.raises(Exception) as exc:
        await service.get_part(db_session, 9999, "test_tenant")
    assert "404" in str(exc.value) or "not found" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_list_parts(db_session):
    await service.create_part(
        db_session,
        schema.PartCreate(part_number="P1", description="Part 1", hsn_code="1", unit_price=100.0),
        "test_tenant",
    )
    await service.create_part(
        db_session,
        schema.PartCreate(part_number="P2", description="Part 2", hsn_code="2", unit_price=200.0),
        "test_tenant",
    )
    parts = await service.list_parts(db_session, "test_tenant")
    assert len(parts) == 2


@pytest.mark.asyncio
async def test_create_and_get_labor_rate(db_session):
    rate_data = schema.LaborRateCreate(
        service_type="brake_service",
        city="Mumbai",
        rate_per_hour=500.0,
        estimated_hours=2.0,
    )
    rate = await service.create_labor_rate(db_session, rate_data, "test_tenant")
    assert rate.id is not None

    retrieved = await service.get_labor_rate(db_session, "brake_service", "Mumbai", "test_tenant")
    # Service returns dict when cached, ORM object when not cached
    if isinstance(retrieved, dict):
        assert retrieved["rate_per_hour"] == 500.0
    else:
        assert retrieved.rate_per_hour == 500.0


@pytest.mark.asyncio
async def test_labor_rate_fallback_to_default_city(db_session):
    await service.create_labor_rate(
        db_session,
        schema.LaborRateCreate(service_type="general", city="default", rate_per_hour=400.0),
        "test_tenant",
    )
    rate = await service.get_labor_rate(db_session, "general", "UnknownCity", "test_tenant")
    assert rate is not None
