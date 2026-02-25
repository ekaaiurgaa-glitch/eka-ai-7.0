import json
from decimal import Decimal
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import date, datetime
from sqlalchemy import select
from app.core.cache import cache_get, cache_set
from . import schema, model

# Fallback Matrices (P1-14)
DEFAULT_WEAR_TEAR = {"annual_parts_cost": 40000, "annual_labor_cost": 20000}
DEFAULT_CITY_INDEX = 1.0

async def _get_mg_formula(db, make: str, model_name: str, fuel: str) -> dict:
    """Fetch formula from DB with local fallback."""
    from .model import MGFormula
    stmt = select(MGFormula).where(
        MGFormula.make == make,
        MGFormula.model == model_name,
        MGFormula.fuel_type == fuel
    )
    result = await db.execute(stmt)
    formula = result.scalar_one_or_none()
    
    if formula:
        return {
            "annual_parts_cost": float(formula.annual_base_cost_inr * formula.parts_pct / 100),
            "annual_labor_cost": float(formula.annual_base_cost_inr * formula.labor_pct / 100)
        }
    return DEFAULT_WEAR_TEAR

async def _get_city_multiplier(db, city: str) -> float:
    """Fetch city index from DB with local fallback."""
    from .model import CityIndex
    stmt = select(CityIndex).where(CityIndex.city == city)
    result = await db.execute(stmt)
    idx = result.scalar_one_or_none()
    return float(idx.multiplier) if idx else DEFAULT_CITY_INDEX

async def calculate_mg_service(db, request: schema.MGCalculationRequest) -> schema.MGCalculationResponse:
    """
    Deterministic MG calculation service.
    """
    costs = await _get_mg_formula(db, request.make, request.model, request.fuel_type.value)
    city_adj = await _get_city_multiplier(db, request.city)
    
    # Calculate Risk Buffer (P1-16)
    # Factor logic from TDD/BRD
    buffer = 0.0
    age = datetime.now().year - request.year
    if age > 7: buffer += 0.10
    elif age >= 5: buffer += 0.05
    
    if request.usage_type == "commercial": buffer += 0.40 # Will be capped
    elif request.usage_type == "ride-sharing": buffer += 0.15
    
    if request.monthly_km > 3000: buffer += 0.08
    elif request.monthly_km >= 2000: buffer += 0.04
    
    if request.warranty_status == "out_of_warranty": buffer += 0.05
    
    # Hard cap at 0.35 (TDD 4.3)
    final_buffer = min(buffer, 0.35)
    
    risk_level = "low"
    if final_buffer > 0.25: risk_level = "high"
    elif final_buffer > 0.15: risk_level = "medium"
    
    # Base calculation
    usage_multiplier = request.monthly_km / 1000.0
    adjusted_parts = costs["annual_parts_cost"] * usage_multiplier
    adjusted_labor = costs["annual_labor_cost"] * city_adj
    
    # Apply risk buffer
    final_annual_cost = (adjusted_parts + adjusted_labor) * (1 + final_buffer)
    
    # Apply warranty discount if applicable
    if request.warranty_status == "under_warranty":
        final_annual_cost *= 0.7 # 30% reduction on MG cost if factory warranty covers major repairs
        
    monthly_mg = final_annual_cost / 12.0

    return schema.MGCalculationResponse(
        annual_parts=round(adjusted_parts, 2),
        annual_labor=round(adjusted_labor, 2),
        city_adj=city_adj,
        risk_adj=1 + final_buffer,
        risk_buffer_pct=round(final_buffer * 100, 2),
        risk_level=risk_level,
        final_annual_cost=round(final_annual_cost, 2),
        monthly_mg=round(monthly_mg, 2),
        notes="Deterministic calculation complete. No AI math used."
    )
