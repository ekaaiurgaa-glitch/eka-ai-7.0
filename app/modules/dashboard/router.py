from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from . import kpi_service
from app.core.dependencies import get_db, get_tenant_id
from app.core.rbac import require_role

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])

@router.get("/workshop")
async def get_workshop_dashboard(
    period_days: int = 30,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["owner", "manager"])),
):
    """
    Returns Workshop KPIs
    """
    return await kpi_service.get_workshop_kpis(tenant_id, period_days)

@router.get("/fleet")
async def get_fleet_dashboard(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["fleet_admin", "manager"])),
):
    """
    Returns Fleet KPIs
    """
    return await kpi_service.get_fleet_kpis(tenant_id)

@router.get("/owner/{vehicle_id}")
async def get_owner_dashboard(
    vehicle_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["customer", "owner"])),
):
    """
    Returns Owner KPIs for a specific vehicle
    """
    return await kpi_service.get_owner_kpis(vehicle_id, tenant_id)