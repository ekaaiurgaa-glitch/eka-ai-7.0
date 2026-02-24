from . import schema
from app.core.cache import cache_get, cache_set

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
