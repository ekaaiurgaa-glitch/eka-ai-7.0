"""MG Financial Risk API Router."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_tenant_id
from app.modules.mg_engine.financial_risk import calculate_reserve, analyze_risk, ReserveCalculation, RiskAnalysis

router = APIRouter(prefix="/mg/financial", tags=["MG Financial"])

@router.post("/reserve/calculate", response_model=ReserveCalculation)
async def calculate_reserve_endpoint(
    contract_value: float,
    risk_level: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    return await calculate_reserve(contract_value, risk_level)

@router.post("/risk/analyze", response_model=RiskAnalysis)
async def analyze_risk_endpoint(
    contract_id: int,
    utilized: float,
    reserve: float,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    return await analyze_risk(contract_id, utilized, reserve)
