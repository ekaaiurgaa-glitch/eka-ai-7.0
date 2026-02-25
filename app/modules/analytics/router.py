"""Unit Economics API Router."""
from fastapi import APIRouter, Depends
from datetime import datetime
from app.core.dependencies import get_tenant_id
from app.modules.analytics.unit_economics import calculate_unit_economics, project_token_usage

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/unit-economics")
async def get_unit_economics(
    start_date: datetime,
    end_date: datetime,
    tenant_id: str = Depends(get_tenant_id)
):
    return await calculate_unit_economics(tenant_id, start_date, end_date)

@router.get("/token-projections")
async def get_token_projections(
    months: int = 6,
    tenant_id: str = Depends(get_tenant_id)
):
    return await project_token_usage(tenant_id, months)
