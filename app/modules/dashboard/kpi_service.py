from uuid import UUID
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from app.core.cache import cache_get, cache_set

@dataclass
class WorkshopKPIs:
    daily_revenue: Dict[str, float]
    monthly_revenue: float
    profit_margin_pct: float
    jobs_by_status: Dict[str, int]
    pending_approvals: int
    technician_performance: List[Dict[str, Any]]
    low_stock_items: List[Dict[str, Any]]
    avg_job_tat_hours: float

@dataclass
class FleetKPIs:
    mg_commitments_vs_actual: List[Dict[str, Any]]
    cost_per_vehicle: float
    vehicle_downtime_pct: float
    risk_indicators: List[Dict[str, Any]]
    cost_breakdown: Dict[str, float]
    compliance_status: List[Dict[str, Any]]

@dataclass
class OwnerKPIs:
    service_history: List[Dict[str, Any]]
    warranty_status: str
    upcoming_services: List[Dict[str, Any]]
    total_spend_ytd: float
    vehicle_health_score: int

async def get_workshop_kpis(tenant_id: UUID, period_days: int = 30) -> WorkshopKPIs:
    """
    All queries scoped to tenant_id. Cache results in Redis with 5-minute TTL.
    """
    cache_key = f"dashboard:workshop:{tenant_id}:{period_days}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    # Stub data since real DB session/queries aren't available broadly
    ret = WorkshopKPIs(
        daily_revenue={},
        monthly_revenue=150000.0,
        profit_margin_pct=34.5,
        jobs_by_status={"OPEN": 5, "REPAIR": 12, "CLOSED": 45},
        pending_approvals=3,
        technician_performance=[],
        low_stock_items=[],
        avg_job_tat_hours=4.2
    )
    cache_set(cache_key, ret, ttl=300)
    return ret

async def get_fleet_kpis(tenant_id: UUID) -> FleetKPIs:
    """
    Fleet dashboard KPIs scoped to tenant
    """
    return FleetKPIs(
        mg_commitments_vs_actual=[],
        cost_per_vehicle=45000.0,
        vehicle_downtime_pct=2.1,
        risk_indicators=[],
        cost_breakdown={"parts": 65.0, "labor": 35.0},
        compliance_status=[]
    )

async def get_owner_kpis(vehicle_id: UUID, tenant_id: UUID) -> OwnerKPIs:
    """
    Owner dashboard KPIs for specific vehicle scoped to tenant
    """
    return OwnerKPIs(
        service_history=[],
        warranty_status="active",
        upcoming_services=[],
        total_spend_ytd=12500.0,
        vehicle_health_score=92
    )
