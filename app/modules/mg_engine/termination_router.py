"""Contract Termination API Router."""
from fastapi import APIRouter, Depends
from datetime import datetime
from app.core.dependencies import get_tenant_id
from app.modules.mg_engine.contract_termination import calculate_prorated_refund, terminate_contract

router = APIRouter(prefix="/mg/contracts", tags=["MG Contracts"])

@router.post("/calculate-refund")
async def calculate_refund(
    contract_value: float,
    start_date: datetime,
    end_date: datetime,
    tenant_id: str = Depends(get_tenant_id)
):
    return await calculate_prorated_refund(contract_value, start_date, end_date)

@router.post("/{contract_id}/terminate")
async def terminate(
    contract_id: int,
    reason: str,
    tenant_id: str = Depends(get_tenant_id)
):
    return await terminate_contract(contract_id, reason)
