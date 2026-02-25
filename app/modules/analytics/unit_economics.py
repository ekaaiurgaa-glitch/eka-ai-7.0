"""Unit Economics & CPTM Tracking."""
from pydantic import BaseModel
from typing import List
from datetime import datetime


class UnitEconomics(BaseModel):
    tenant_id: str
    period: str
    total_revenue: float
    total_costs: float
    gross_margin: float
    gross_margin_pct: float
    cptm: float
    token_cost: float
    infrastructure_cost: float
    avg_revenue_per_tenant: float


class TokenProjection(BaseModel):
    month: str
    estimated_tokens: int
    estimated_cost: float
    revenue_projection: float
    margin_projection: float


async def calculate_unit_economics(tenant_id: str, start_date: datetime, end_date: datetime) -> UnitEconomics:
    total_revenue = 50000.0
    token_cost = 5000.0
    infra_cost = 3000.0
    total_costs = token_cost + infra_cost
    gross_margin = total_revenue - total_costs
    
    return UnitEconomics(
        tenant_id=tenant_id,
        period=f"{start_date.date()} to {end_date.date()}",
        total_revenue=total_revenue,
        total_costs=total_costs,
        gross_margin=gross_margin,
        gross_margin_pct=(gross_margin / total_revenue * 100) if total_revenue > 0 else 0,
        cptm=(token_cost / (total_revenue / 1000)) if total_revenue > 0 else 0,
        token_cost=token_cost,
        infrastructure_cost=infra_cost,
        avg_revenue_per_tenant=total_revenue
    )


async def project_token_usage(tenant_id: str, months: int = 6) -> List[TokenProjection]:
    projections = []
    base_tokens = 100000
    base_cost = 1000.0
    
    for i in range(months):
        growth_factor = 1 + (i * 0.15)
        projections.append(TokenProjection(
            month=f"Month {i+1}",
            estimated_tokens=int(base_tokens * growth_factor),
            estimated_cost=base_cost * growth_factor,
            revenue_projection=base_cost * growth_factor * 5,
            margin_projection=base_cost * growth_factor * 4
        ))
    
    return projections
