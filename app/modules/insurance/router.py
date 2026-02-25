"""Insurance API Router."""
from fastapi import APIRouter, Depends
from app.core.dependencies import get_tenant_id
from app.modules.insurance.integration import get_insurance_quote, bind_policy

router = APIRouter(prefix="/insurance", tags=["Insurance"])

@router.get("/quote")
async def quote(
    vehicle_id: int,
    coverage: float,
    tenant_id: str = Depends(get_tenant_id)
):
    return await get_insurance_quote(vehicle_id, coverage)

@router.post("/bind")
async def bind(
    quote_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    return await bind_policy(quote_id)
