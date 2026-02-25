from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import require_permission

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/parts", response_model=List[schema.Part])
async def list_parts(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_estimates")),
):
    """List all parts in the catalog."""
    return await service.list_parts(db, tenant_id)


@router.get("/parts/{part_id}", response_model=schema.Part)
async def get_part(
    part_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_estimates")),
):
    """Get a specific part by ID."""
    return await service.get_part(db, part_id, tenant_id)


@router.post("/parts", response_model=schema.Part)
async def create_part(
    part: schema.PartCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_catalog")),
):
    """Add a new part to the catalog (admin)."""
    return await service.create_part(db, part, tenant_id)


@router.post("/labor-rates", response_model=schema.LaborRate)
async def create_labor_rate(
    rate: schema.LaborRateCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_catalog")),
):
    """Add a new labor rate (admin)."""
    return await service.create_labor_rate(db, rate, tenant_id)
