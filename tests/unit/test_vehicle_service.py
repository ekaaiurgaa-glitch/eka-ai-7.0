import pytest
from app.modules.vehicles import service, schema


@pytest.mark.asyncio
async def test_create_vehicle(db_session):
    vehicle_data = schema.VehicleCreate(
        plate_number="MH12AB1234",
        make="Maruti",
        model="Swift",
        variant="VXI",
        year=2019,
        fuel_type=schema.FuelType.petrol,
        owner_name="John Doe",
        monthly_km=1200,
    )
    vehicle = await service.create_vehicle(db_session, vehicle_data, "test_tenant")
    assert vehicle.id is not None
    assert vehicle.plate_number == "MH12AB1234"
    assert vehicle.make == "Maruti"


@pytest.mark.asyncio
async def test_get_vehicle(db_session):
    vehicle_data = schema.VehicleCreate(
        plate_number="KA01XY9999",
        make="Honda",
        model="City",
        variant="VX",
        year=2020,
        fuel_type=schema.FuelType.diesel,
    )
    created = await service.create_vehicle(db_session, vehicle_data, "test_tenant")
    retrieved = await service.get_vehicle(db_session, created.id, "test_tenant")
    assert retrieved.plate_number == "KA01XY9999"


@pytest.mark.asyncio
async def test_list_vehicles(db_session):
    await service.create_vehicle(
        db_session,
        schema.VehicleCreate(plate_number="V1", make="M1", model="M1", variant="Base", year=2020, fuel_type=schema.FuelType.petrol),
        "test_tenant",
    )
    await service.create_vehicle(
        db_session,
        schema.VehicleCreate(plate_number="V2", make="M2", model="M2", variant="Top", year=2021, fuel_type=schema.FuelType.diesel),
        "test_tenant",
    )
    vehicles = await service.list_vehicles(db_session, "test_tenant")
    assert len(vehicles) == 2


@pytest.mark.asyncio
async def test_update_vehicle(db_session):
    vehicle = await service.create_vehicle(
        db_session,
        schema.VehicleCreate(plate_number="UP01AB1234", make="Tata", model="Nexon", variant="EV", year=2022, fuel_type=schema.FuelType.electric),
        "test_tenant",
    )
    update_data = schema.VehicleUpdate(owner_name="Jane Doe", monthly_km=1500)
    updated = await service.update_vehicle(db_session, vehicle.id, update_data, "test_tenant")
    assert updated.owner_name == "Jane Doe"
    assert updated.monthly_km == 1500
