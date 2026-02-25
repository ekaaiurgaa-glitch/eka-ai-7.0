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
