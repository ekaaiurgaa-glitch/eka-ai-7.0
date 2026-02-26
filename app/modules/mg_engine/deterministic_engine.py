import json
from decimal import Decimal
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import date, datetime
from sqlalchemy import select
from app.core.cache import cache_get, cache_set
from . import schema

# ── Fallback Matrices ──────────────────────────────────────────────
# Used when DB tables (mg_formulas, city_indices) have no matching row.
# Production: rows seeded via admin panel or migration.
WEAR_TEAR_MATRIX = {
    "Tata_Nexon_diesel": {"annual_parts_cost": 48000, "annual_labor_cost": 24000},
    "Tata_Nexon_XZ+_diesel": {"annual_parts_cost": 52000, "annual_labor_cost": 26000},
    "default": {"annual_parts_cost": 40000, "annual_labor_cost": 20000},
}

CITY_LABOR_INDEX = {
    "Mumbai": 1.15,
    "default": 1.0,
}

RISK_MULTIPLIER = {
    "commercial": 1.10,
    "personal": 1.0,
    "default": 1.0,
}

# ── Dataclasses ────────────────────────────────────────────────────
@dataclass
class ReserveAllocation:
    reserve_deposited: Decimal
    operating_revenue: Decimal

@dataclass
class OverrunResult:
    overrun_pct: float
    actual_cost: Decimal
    mg_fee: Decimal
    recommended_action: str

@dataclass
class RepricingRecommendation:
    current_fee: Decimal
    recommended_fee: Decimal
    action: str
    reason: str

# ── Sync helpers (used by unit tests & cache layer) ────────────────
def _get_wear_tear_costs(vehicle_key: str) -> dict:
    """Cached lookup for wear-tear matrix."""
    cache_key = f"wear_tear:{vehicle_key}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    costs = WEAR_TEAR_MATRIX.get(vehicle_key, WEAR_TEAR_MATRIX["default"])
    cache_set(cache_key, costs, ttl=3600)
    return costs

def _get_city_labor_index(city: str) -> float:
    """Cached lookup for city labor index."""
    cache_key = f"city_labor:{city}"
    cached = cache_get(cache_key)
    if cached:
        return cached["index"]
    index = CITY_LABOR_INDEX.get(city, CITY_LABOR_INDEX["default"])
    cache_set(cache_key, {"index": index}, ttl=3600)
    return index

# ── Sync calculate_mg (backward compat for unit tests) ─────────────
def calculate_mg(request: schema.MGCalculationRequest) -> schema.MGCalculationResponse:
    """
    Pure-sync deterministic MG calculation using in-memory matrices.
    """
    vehicle_key_parts = [request.make, request.model]
    if request.variant:
        vehicle_key_parts.append(request.variant)
    vehicle_key_parts.append(request.fuel_type.value)
    vehicle_key = "_".join(vehicle_key_parts)
    wear_tear_costs = _get_wear_tear_costs(vehicle_key)

    annual_parts = wear_tear_costs["annual_parts_cost"]
    annual_labor = wear_tear_costs["annual_labor_cost"]

    usage_multiplier = request.monthly_km / 1000
    annual_parts *= usage_multiplier

    city_adj = _get_city_labor_index(request.city)
    risk_adj = RISK_MULTIPLIER.get(request.usage_type, RISK_MULTIPLIER["default"])

    warranty_adj = 0.0
    if request.warranty_status == "under_warranty":
        warranty_adj = 0.5

    final_annual_cost = (annual_parts + (annual_labor * city_adj)) * risk_adj * (1 - warranty_adj)
    monthly_mg = final_annual_cost / 12

    # Compute risk buffer & level for response
    buffer = calculate_risk_buffer(
        {"age_years": datetime.now().year - request.year},
        {
            "usage_type": request.usage_type.value if hasattr(request.usage_type, 'value') else request.usage_type,
            "monthly_km": request.monthly_km,
            "warranty_status": "expired" if request.warranty_status == "out_of_warranty" else "active",
        }
    )
    risk_level = "low"
    if buffer > 0.25: risk_level = "high"
    elif buffer > 0.15: risk_level = "medium"

    return schema.MGCalculationResponse(
        annual_parts=annual_parts,
        annual_labor=annual_labor,
        city_adj=city_adj,
        risk_adj=risk_adj,
        risk_buffer_pct=round(buffer * 100, 2),
        risk_level=risk_level,
        final_annual_cost=round(final_annual_cost, 2),
        monthly_mg=round(monthly_mg, 2),
        notes="Final MG calculation must be executed by deterministic financial engine. AI cannot compute financial projections directly.",
    )

# ── Risk Buffer ────────────────────────────────────────────────────
def calculate_risk_buffer(vehicle: Dict[str, Any], usage_profile: Dict[str, Any]) -> float:
    """
    Returns risk buffer as decimal (0.10 to 0.35 max).
    All factors are additive. Hard cap at 0.35.
    """
    buffer = 0.0
    age = vehicle.get("age_years", 0)
    if age > 7:
        buffer += 0.10
    elif age >= 5:
        buffer += 0.05

    usage_type = usage_profile.get("usage_type", "personal")
    if usage_type == "commercial":
        buffer += 0.40
    elif usage_type == "ride-sharing":
        buffer += 0.15

    monthly_km = usage_profile.get("monthly_km", 0)
    if monthly_km > 3000:
        buffer += 0.08
    elif monthly_km >= 2000:
        buffer += 0.04

    if usage_profile.get("warranty_status") == "expired":
        buffer += 0.05

    if usage_profile.get("hilly_terrain", False):
        buffer += 0.05

    if usage_profile.get("poor_maintenance_history", False):
        buffer += 0.10

    return min(buffer, 0.35)

# ── Reserve Allocation ─────────────────────────────────────────────
def allocate_reserve(tenant_id: str, mg_contract_id: str, payment_amount_inr: Decimal, risk_level: str) -> ReserveAllocation:
    pct = 0.10
    if risk_level == "medium":
        pct = 0.20
    elif risk_level == "high":
        pct = 0.30
    reserve_deposited = payment_amount_inr * Decimal(str(pct))
    operating_revenue = payment_amount_inr - reserve_deposited
    return ReserveAllocation(
        reserve_deposited=round(reserve_deposited, 2),
        operating_revenue=round(operating_revenue, 2)
    )

# ── Overrun Detection ──────────────────────────────────────────────
def check_overrun(mg_contract_id: str, current_month, actual_cost: Decimal, mg_fee: Decimal) -> Optional[OverrunResult]:
    if mg_fee <= 0:
        return None
    try:
        overrun_ratio = float(actual_cost / mg_fee)
    except:
        overrun_ratio = 0.0
    if overrun_ratio > 1.5:
        pct = (overrun_ratio - 1.0) * 100
        return OverrunResult(
            overrun_pct=round(pct, 2),
            actual_cost=actual_cost,
            mg_fee=mg_fee,
            recommended_action="Review vehicle repair history and consider contract termination or repricing."
        )
    return None

# ── Repricing ──────────────────────────────────────────────────────
def recommend_repricing(mg_contract_id: str, monthly_fee: Decimal, avg_monthly_cost: Decimal, risk_buffer: float) -> RepricingRecommendation:
    recommended_fee = avg_monthly_cost * Decimal(str(1 + risk_buffer))
    if recommended_fee > monthly_fee * Decimal("1.10"):
        action = "increase"
        reason = "Actual costs significantly exceed current fee."
    elif recommended_fee < monthly_fee * Decimal("0.90"):
        action = "decrease"
        reason = "Actual costs are lower than current fee. Room for competitive discount."
    else:
        action = "maintain"
        reason = "Current fee is optimal within 10% tolerance."
    return RepricingRecommendation(
        current_fee=monthly_fee,
        recommended_fee=round(recommended_fee, 2),
        action=action,
        reason=reason
    )

# ── Async DB-backed version (production path) ──────────────────────
async def calculate_mg_service(db, request: schema.MGCalculationRequest) -> schema.MGCalculationResponse:
    """
    Async version that queries DB for formulas and city indices.
    Falls back to in-memory matrices if DB rows are missing.
    """
    from . import model as mg_model
    
    stmt = select(mg_model.MGFormula).where(
        mg_model.MGFormula.make == request.make,
        mg_model.MGFormula.model == request.model,
        mg_model.MGFormula.fuel_type == request.fuel_type.value
    )
    if request.variant:
        stmt = stmt.where(mg_model.MGFormula.variant == request.variant)

    result = await db.execute(stmt)
    formula = result.scalar_one_or_none()

    if formula:
        costs = {
            "annual_parts_cost": float(formula.annual_base_cost_inr * formula.parts_pct / 100),
            "annual_labor_cost": float(formula.annual_base_cost_inr * formula.labor_pct / 100)
        }
    else:
        vehicle_key_parts = [request.make, request.model]
        if request.variant:
            vehicle_key_parts.append(request.variant)
        vehicle_key_parts.append(request.fuel_type.value)
        vehicle_key = "_".join(vehicle_key_parts)
        costs = WEAR_TEAR_MATRIX.get(vehicle_key, WEAR_TEAR_MATRIX["default"])

    # City index from DB
    stmt2 = select(mg_model.CityIndex).where(mg_model.CityIndex.city == request.city)
    result2 = await db.execute(stmt2)
    idx = result2.scalar_one_or_none()
    city_adj = float(idx.multiplier) if idx else _get_city_labor_index(request.city)

    # Risk buffer calculation
    buffer = calculate_risk_buffer(
        {"age_years": datetime.now().year - request.year},
        {
            "usage_type": request.usage_type.value if hasattr(request.usage_type, 'value') else request.usage_type,
            "monthly_km": request.monthly_km,
            "warranty_status": "expired" if request.warranty_status == "out_of_warranty" else "active",
        }
    )
    risk_level = "low"
    if buffer > 0.25: risk_level = "high"
    elif buffer > 0.15: risk_level = "medium"

    usage_multiplier = request.monthly_km / 1000.0
    adjusted_parts = costs["annual_parts_cost"] * usage_multiplier
    adjusted_labor = costs["annual_labor_cost"] * city_adj
    risk_adj = RISK_MULTIPLIER.get(
        request.usage_type.value if hasattr(request.usage_type, 'value') else request.usage_type,
        RISK_MULTIPLIER["default"]
    )

    final_annual_cost = (adjusted_parts + (adjusted_labor)) * risk_adj
    if request.warranty_status == "under_warranty":
        final_annual_cost *= 0.5

    monthly_mg = final_annual_cost / 12.0

    return schema.MGCalculationResponse(
        annual_parts=round(adjusted_parts, 2),
        annual_labor=round(adjusted_labor, 2),
        city_adj=city_adj,
        risk_adj=risk_adj,
        risk_buffer_pct=round(buffer * 100, 2),
        risk_level=risk_level,
        final_annual_cost=round(final_annual_cost, 2),
        monthly_mg=round(monthly_mg, 2),
        notes="Deterministic calculation complete. No AI math used."
    )
