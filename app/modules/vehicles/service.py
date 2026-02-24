from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from . import model, schema


async def create_vehicle(db: AsyncSession, vehicle: schema.VehicleCreate, tenant_id: str) -> model.Vehicle:
    db_vehicle = model.Vehicle(**vehicle.model_dump(), tenant_id=tenant_id)
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle


async def get_vehicle(db: AsyncSession, vehicle_id: int, tenant_id: str) -> model.Vehicle:
    result = await db.execute(
        select(model.Vehicle).filter(
            model.Vehicle.id == vehicle_id, model.Vehicle.tenant_id == tenant_id
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


async def list_vehicles(db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 50) -> List[model.Vehicle]:
    result = await db.execute(
        select(model.Vehicle)
        .filter(model.Vehicle.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_vehicle(db: AsyncSession, vehicle_id: int, update: schema.VehicleUpdate, tenant_id: str) -> model.Vehicle:
    vehicle = await get_vehicle(db, vehicle_id, tenant_id)
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle
