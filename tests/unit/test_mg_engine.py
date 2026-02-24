from app.modules.mg_engine.deterministic_engine import calculate_mg
from app.modules.mg_engine.schema import MGCalculationRequest

def test_mg_calculation_tata_nexon():
    """
    Tests the MG calculation for a specific vehicle to ensure deterministic output.
    This test should fail only if the underlying matrices are intentionally changed.
    """
    request = MGCalculationRequest(
        make="Tata",
        model="Nexon",
        year=2021,
        fuel_type="diesel",
        city="Mumbai",
        monthly_km=2500,
        warranty_status="out_of_warranty",
        usage_type="commercial",
        tenant_id="test_tenant"
    )

    response = calculate_mg(request)

    assert response.annual_parts == 48000
    assert response.annual_labor == 24000
    assert response.city_adj == 1.15
    assert response.risk_adj == 1.10
    assert response.final_annual_cost == 83160.00
    assert response.monthly_mg == 6930.00
