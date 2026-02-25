"""MG Financial Risk & Reserve Fund Model."""
from pydantic import BaseModel


class ReserveCalculation(BaseModel):
    contract_value: float
    risk_buffer_pct: float
    reserve_amount: float
    monthly_allocation: float


class RiskAnalysis(BaseModel):
    contract_id: int
    utilization_pct: float
    overrun_risk: str
    recommended_action: str


async def calculate_reserve(contract_value: float, risk_level: str) -> ReserveCalculation:
    risk_buffers = {"low": 0.10, "medium": 0.15, "high": 0.25}
    buffer_pct = risk_buffers.get(risk_level, 0.15)
    reserve = contract_value * buffer_pct
    monthly = reserve / 12
    
    return ReserveCalculation(
        contract_value=contract_value,
        risk_buffer_pct=buffer_pct,
        reserve_amount=reserve,
        monthly_allocation=monthly
    )


async def analyze_risk(contract_id: int, utilized: float, reserve: float) -> RiskAnalysis:
    utilization = (utilized / reserve * 100) if reserve > 0 else 0
    
    if utilization > 90:
        risk = "critical"
        action = "Increase reserve or renegotiate contract"
    elif utilization > 70:
        risk = "high"
        action = "Monitor closely, prepare contingency"
    elif utilization > 50:
        risk = "medium"
        action = "Continue monitoring"
    else:
        risk = "low"
        action = "Normal operations"
    
    return RiskAnalysis(
        contract_id=contract_id,
        utilization_pct=utilization,
        overrun_risk=risk,
        recommended_action=action
    )
