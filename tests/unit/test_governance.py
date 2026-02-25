import pytest
from app.ai.governance import domain_gate, context_gate, confidence_gate
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_domain_gate_allows_automobile_queries():
    await domain_gate("My car engine is overheating")
    await domain_gate("Brake pads need replacement")
    await domain_gate("Check engine light is on")


@pytest.mark.asyncio
async def test_domain_gate_rejects_non_automobile():
    with pytest.raises(HTTPException) as exc:
        await domain_gate("What is the weather today?")
    assert exc.value.status_code == 403
    assert "DOMAIN_GATE_DENY" in exc.value.detail


def test_context_gate_passes_with_vehicle():
    vehicle = {"make": "Maruti", "model": "Swift", "year": 2019, "fuel_type": "petrol"}
    context_gate("Engine overheating issue", vehicle)


def test_context_gate_fails_without_vehicle_for_diagnostic():
    with pytest.raises(HTTPException) as exc:
        context_gate("My brake is making noise", None)
    assert "CONTEXT_REQUEST" in exc.value.detail


def test_context_gate_allows_general_query_without_vehicle():
    context_gate("What causes engine overheating?", None)


def test_confidence_gate_passes_high_confidence():
    confidence_gate(95.0)
    confidence_gate(92.0)


def test_confidence_gate_fails_low_confidence():
    with pytest.raises(HTTPException) as exc:
        confidence_gate(45.0)
    assert "REQUEST_CLARIFICATION" in exc.value.detail
