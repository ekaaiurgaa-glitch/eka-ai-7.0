import pytest
from decimal import Decimal
from app.modules.mg_engine import schema, deterministic_engine

def test_base_cost_lookup_maruti_swift_petrol():
    res = deterministic_engine._get_wear_tear_costs("Maruti_Swift_petrol")
    assert "annual_parts_cost" in res

def test_city_multiplier_tier1_is_1_15():
    assert deterministic_engine._get_city_labor_index("Mumbai") == 1.15

def test_city_multiplier_default_is_1_0():
    assert deterministic_engine._get_city_labor_index("Unknown") == 1.0

def test_monthly_km_3000_adds_risk():
    profile = {"monthly_km": 3001}
    assert 0.08 <= deterministic_engine.calculate_risk_buffer({}, profile)

def test_commercial_usage_adds_40_pct_risk_capped_at_35():
    profile = {"usage_type": "commercial"}
    assert deterministic_engine.calculate_risk_buffer({}, profile) == 0.35

def test_risk_buffer_caps_at_35_pct():
    profile = {"usage_type": "commercial", "monthly_km": 5000}
    vehicle = {"age_years": 8}
    assert deterministic_engine.calculate_risk_buffer(vehicle, profile) == 0.35

def test_warranty_expired_adds_5_pct_risk():
    profile = {"warranty_status": "expired"}
    assert deterministic_engine.calculate_risk_buffer({}, profile) == 0.05

def test_vehicle_age_7_plus_adds_10_pct_risk():
    vehicle = {"age_years": 8}
    assert deterministic_engine.calculate_risk_buffer(vehicle, {}) == 0.10

def test_reserve_allocation_low_risk_10_pct():
    res = deterministic_engine.allocate_reserve("tenant-1", "contract-1", Decimal("1000.00"), "low")
    assert res.reserve_deposited == Decimal("100.00")
    assert res.operating_revenue == Decimal("900.00")

def test_reserve_allocation_high_risk_30_pct():
    res = deterministic_engine.allocate_reserve("tenant-1", "contract-1", Decimal("1000.00"), "high")
    assert res.reserve_deposited == Decimal("300.00")

def test_overrun_detected_at_150_pct_of_fee():
    res = deterministic_engine.check_overrun("contract-1", None, Decimal("1600.00"), Decimal("1000.00"))
    assert res is not None
    assert res.overrun_pct == 60.0

def test_overrun_below_150_pct_no_alert():
    res = deterministic_engine.check_overrun("contract-1", None, Decimal("1400.00"), Decimal("1000.00"))
    assert res is None

def test_repricing_increase_recommendation():
    res = deterministic_engine.recommend_repricing("contract-1", Decimal("1000"), Decimal("2000"), 0.10)
    assert res.action == "increase"
    assert res.recommended_fee == Decimal("2200.00")

def test_repricing_decrease_recommendation():
    res = deterministic_engine.recommend_repricing("contract-1", Decimal("2000"), Decimal("1000"), 0.10)
    assert res.action == "decrease"

def test_repricing_maintain_recommendation():
    res = deterministic_engine.recommend_repricing("contract-1", Decimal("1000"), Decimal("950"), 0.10)
    assert res.action == "maintain"
