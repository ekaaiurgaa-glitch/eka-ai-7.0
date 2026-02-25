from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import require_permission

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("", response_model=schema.Vehicle)
async def create_vehicle(
    vehicle: schema.VehicleCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_vehicles")),
):
    """Register a new vehicle."""
    return await service.create_vehicle(db, vehicle, tenant_id)


@router.get("", response_model=List[schema.Vehicle])
async def list_vehicles(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_vehicles")),
):
    """List all vehicles for the current tenant."""
    return await service.list_vehicles(db, tenant_id, skip, limit)


@router.get("/{vehicle_id}", response_model=schema.Vehicle)
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_vehicles")),
):
    """Get a vehicle by ID."""
    return await service.get_vehicle(db, vehicle_id, tenant_id)


@router.patch("/{vehicle_id}", response_model=schema.Vehicle)
async def update_vehicle(
    vehicle_id: int,
    update: schema.VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_vehicles")),
):
    """Update vehicle details."""
    return await service.update_vehicle(db, vehicle_id, update, tenant_id)
