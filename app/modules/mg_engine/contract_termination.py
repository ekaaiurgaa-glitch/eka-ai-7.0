"""MG contract termination and refunds."""
from datetime import datetime
from pydantic import BaseModel


class TerminationRequest(BaseModel):
    contract_id: int
    reason: str
    effective_date: datetime


class RefundCalculation(BaseModel):
    contract_value: float
    months_used: int
    months_total: int
    refund_amount: float
    reserve_release: float


async def calculate_prorated_refund(contract_value: float, start_date: datetime, end_date: datetime) -> RefundCalculation:
    months_total = 12
    months_used = (end_date - start_date).days // 30
    months_remaining = max(0, months_total - months_used)
    
    refund = (contract_value / months_total) * months_remaining * 0.9
    reserve_release = contract_value * 0.15
    
    return RefundCalculation(
        contract_value=contract_value,
        months_used=months_used,
        months_total=months_total,
        refund_amount=refund,
        reserve_release=reserve_release
    )


async def terminate_contract(contract_id: int, reason: str) -> dict:
    return {
        "termination_id": f"term_{contract_id}",
        "status": "completed",
        "refund_processed": True,
        "reserve_released": True
    }
