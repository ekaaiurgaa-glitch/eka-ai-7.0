"""Insurance integration."""
from pydantic import BaseModel

class InsuranceQuote(BaseModel):
    vehicle_id: int
    coverage_amount: float
    premium: float
    provider: str

async def get_insurance_quote(vehicle_id: int, coverage: float) -> InsuranceQuote:
    return InsuranceQuote(
        vehicle_id=vehicle_id,
        coverage_amount=coverage,
        premium=coverage * 0.05,
        provider="HDFC ERGO"
    )


class PolicyBinding(BaseModel):
    policy_id: str
    vehicle_id: int
    coverage_amount: float
    premium: float
    status: str


async def bind_policy(quote_id: str, vehicle_id: int) -> PolicyBinding:
    return PolicyBinding(
        policy_id=f"POL{hash(quote_id) % 100000}",
        vehicle_id=vehicle_id,
        coverage_amount=500000.0,
        premium=25000.0,
        status="active"
    )
