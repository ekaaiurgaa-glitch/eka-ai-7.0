import json
from decimal import Decimal
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import date, timedelta
from app.core.cache import cache_get, cache_set
from . import schema

# These matrices and indices would be loaded from a database or a configuration file in a real application.
WEAR_TEAR_MATRIX = {
    "Tata_Nexon_diesel": {"annual_parts_cost": 48000, "annual_labor_cost": 24000},
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

def calculate_mg(request: schema.MGCalculationRequest) -> schema.MGCalculationResponse:
    """
    Calculates the Maintenance Guarantee (MG) amount based on deterministic rules.
    This function must not use any LLMs or other non-deterministic components.
    Uses Redis caching for matrix lookups when available.
    """
    vehicle_key = f"{request.make}_{request.model}_{request.fuel_type.value}"
    wear_tear_costs = _get_wear_tear_costs(vehicle_key)

    annual_parts = wear_tear_costs["annual_parts_cost"]
    annual_labor = wear_tear_costs["annual_labor_cost"]
    
    # Usage-based adjustment (NEW)
    usage_multiplier = request.monthly_km / 1000  # Base: 1000 km/month
    annual_parts *= usage_multiplier

    city_adj = _get_city_labor_index(request.city)
    risk_adj = RISK_MULTIPLIER.get(request.usage_type, RISK_MULTIPLIER["default"])

    # In a real app, warranty adjustment would be more complex
    warranty_adj = 0.0
    if request.warranty_status == "under_warranty":
        warranty_adj = 0.5  # 50% discount on some parts/labor

    final_annual_cost = (annual_parts + (annual_labor * city_adj)) * risk_adj * (1 - warranty_adj)
    monthly_mg = final_annual_cost / 12

    return schema.MGCalculationResponse(
        annual_parts=annual_parts,
        annual_labor=annual_labor,
        city_adj=city_adj,
        risk_adj=risk_adj,
        final_annual_cost=round(final_annual_cost, 2),
        monthly_mg=round(monthly_mg, 2),
        notes="Final MG calculation must be executed by deterministic financial engine. AI cannot compute financial projections directly.",
    )

def calculate_risk_buffer(vehicle: Dict[str, Any], usage_profile: Dict[str, Any]) -> float:
    """
    Returns risk buffer as decimal (0.10 to 0.35 max).
    All factors are additive. Hard cap at 0.35.
    
    Factors:
    - Age > 7 years:           +0.10
    - Age 5-7 years:           +0.05
    - Commercial usage:        +0.40 (but capped overall at 0.35)
    - Ride-sharing usage:      +0.15
    - Monthly KM > 3000:       +0.08
    - Monthly KM 2000-3000:    +0.04
    - Warranty expired:        +0.05
    - Hilly terrain city:      +0.05
    - Poor maintenance history: +0.10
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

    # Hard cap at 0.35
    return min(buffer, 0.35)

def allocate_reserve(tenant_id: str, mg_contract_id: str, payment_amount_inr: Decimal, risk_level: str) -> ReserveAllocation:
    """
    Reserve percentages: low=10%, medium=20%, high=30%
    Deposit to mg_reserve_accounts (upsert balance)
    Log to mg_reserve_transactions
    Return: ReserveAllocation(reserve_deposited, operating_revenue)
    """
    pct = 0.10
    if risk_level == "medium":
        pct = 0.20
    elif risk_level == "high":
        pct = 0.30
        
    reserve_deposited = payment_amount_inr * Decimal(str(pct))
    operating_revenue = payment_amount_inr - reserve_deposited
    
    # In a real application, this would do database operations using SQLAlchemy session
    # updating ReserveAccount and creating a ReserveTransaction.
    
    return ReserveAllocation(
        reserve_deposited=round(reserve_deposited, 2),
        operating_revenue=round(operating_revenue, 2)
    )

def check_overrun(mg_contract_id: str, current_month: date, actual_cost: Decimal, mg_fee: Decimal) -> Optional[OverrunResult]:
    """
    Sum all job_cards.total_cost for this vehicle in given month (covered by MG).
    Compare to mg_contracts.monthly_fee_inr.
    If actual_cost > monthly_fee * 1.5: emit alert to RabbitMQ queue 'mg.overrun.alerts'
    Return OverrunResult with overrun_pct, actual_cost, mg_fee, recommended_action
    """
    if mg_fee <= 0:
        return None
        
    try:
        overrun_ratio = float(actual_cost / mg_fee)
    except:
        overrun_ratio = 0.0
        
    if overrun_ratio > 1.5:
        # We would emit alert to RabbitMQ queue 'mg.overrun.alerts' here
        pct = (overrun_ratio - 1.0) * 100
        return OverrunResult(
            overrun_pct=round(pct, 2),
            actual_cost=actual_cost,
            mg_fee=mg_fee,
            recommended_action="Review vehicle repair history and consider contract termination or repricing."
        )
    return None

async def run_monthly_reconciliation(tenant_id: str, report_month: date, db_session) -> Any:
    """
    For each active mg_contract in tenant:
    - Sum actual maintenance costs from job_cards (that month)
    - Compare to mg_fee
    - Calculate surplus/deficit per contract
    - Aggregate portfolio totals
    - Update mg_reserve_accounts balance
    - Write mg_reconciliation_reports record
    - Generate PDF report (use reportlab or weasyprint)
    - Upload PDF to S3, store URL
    - Send email via RabbitMQ notification queue
    """
    # This is a stubbed aggregator for demonstration
    # It would query DB in an actual implementation
    
    pass

def recommend_repricing(mg_contract_id: str, monthly_fee: Decimal, avg_monthly_cost: Decimal, risk_buffer: float) -> RepricingRecommendation:
    """
    Look at last 12 months of actual costs for this vehicle.
    avg_monthly_cost = sum / 12
    recommended_fee = avg_monthly_cost * (1 + risk_buffer)
    """
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
