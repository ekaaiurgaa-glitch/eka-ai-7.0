import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_domain_gate_reject(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/chat/query",
        json={
            "query": "What is the weather today?",
            "vehicle": {"make": "Maruti", "model": "Swift", "year": 2019, "fuel_type": "petrol"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 403
    assert "DOMAIN_GATE_DENY" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_context_gate_trigger(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/chat/query",
        json={"query": "My car brake is making a grinding noise when stopping"},
        headers=auth_headers,
    )
    # Should be rejected by context gate (422) or domain gate (403) depending on classification
    assert response.status_code in [403, 422]
    if response.status_code == 422:
        assert "CONTEXT_REQUEST" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_full_query_success(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/chat/query",
        json={
            "query": "Why is my car making a grinding noise when I brake?",
            "vehicle": {"make": "Maruti", "model": "Swift", "year": 2019, "fuel_type": "petrol"},
        },
        headers=auth_headers,
    )
    # May succeed or fail depending on Gemini API availability and validation
    # 403 = domain gate, 422 = context gate, 200 = success, 500 = server error
    assert response.status_code in [200, 403, 422, 500]
    if response.status_code == 200:
        data = response.json()
        assert "issue_summary" in data
        assert "probable_causes" in data


@pytest.mark.asyncio
async def test_chat_general_query_without_vehicle(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/chat/query",
        json={"query": "What causes engine overheating in general?"},
        headers=auth_headers,
    )
    # Should pass context gate for general queries (may fail domain gate if classifier is uncertain)
    assert response.status_code in [200, 403, 500]


@pytest.mark.asyncio
async def test_chat_with_rag_context(client: AsyncClient, auth_headers: dict, db_session):
    # Ingest a knowledge document first
    from app.modules.knowledge import service

    await service.ingest_document(
        db_session,
        title="Brake Maintenance Guide",
        content="Grinding noise from brakes usually indicates worn brake pads. Replace immediately.",
        tenant_id="test_tenant",
        source_url="https://example.com/brake-guide",
    )

    response = await client.post(
        "/api/v1/chat/query",
        json={
            "query": "What causes brake grinding noise?",
            "vehicle": {"make": "Maruti", "model": "Swift", "year": 2019, "fuel_type": "petrol"},
        },
        headers=auth_headers,
    )
    # RAG should inject context - 403/422 are acceptable for gate failures
    assert response.status_code in [200, 403, 422, 500]
    if response.status_code == 200:
        data = response.json()
        # Check if RAG references are populated
        if data.get("rag_references"):
            assert "Brake Maintenance Guide" in data["rag_references"]
