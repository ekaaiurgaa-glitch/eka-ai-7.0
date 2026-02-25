"""Claims Reconciliation API Router."""
from fastapi import APIRouter, Depends
from app.core.dependencies import get_tenant_id
from app.modules.mg_engine.claims_reconciliation import generate_monthly_report, reconcile_claims

router = APIRouter(prefix="/mg/claims", tags=["MG Claims"])

@router.get("/report/{month}")
async def monthly_report(
    month: str,
    tenant_id: str = Depends(get_tenant_id)
):
    return await generate_monthly_report(tenant_id, month)

@router.post("/{contract_id}/reconcile")
async def reconcile(
    contract_id: int,
    tenant_id: str = Depends(get_tenant_id)
):
    return await reconcile_claims(contract_id)
