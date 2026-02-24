"""Integration tests for job card summarization endpoint."""
import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_summarize_job_card_endpoint(async_client, auth_token, test_job_card):
    """Test POST /job-cards/{id}/summarize endpoint."""
    mock_ai_result = '{"technical_summary": "Brake pads at 2mm, replacement required.", "customer_summary": "Your brake pads are worn and need replacement for safety.", "urgency": "high", "estimated_cost": 4500, "recommended_action": "Schedule brake service within 1 week."}'
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = mock_ai_result
        
        response = await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == test_job_card["id"]
    assert data["job_no"] == test_job_card["job_no"]
    assert "technical_summary" in data
    assert "customer_summary" in data
    assert data["urgency"] in ["low", "medium", "high", "critical"]
    assert "estimated_cost" in data
    assert "recommended_action" in data
    assert "cached" in data
    assert "generated_at" in data


@pytest.mark.asyncio
async def test_summarize_caching(async_client, auth_token, test_job_card):
    """Test that second call returns cached result."""
    mock_ai_result = '{"technical_summary": "Test", "customer_summary": "Test2", "urgency": "medium", "estimated_cost": 1000, "recommended_action": "Act"}'
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = mock_ai_result
        
        # First call - should hit AI
        response1 = await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["cached"] is False
        
        # Second call - should return cached
        response2 = await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["cached"] is True
        assert data2["technical_summary"] == data1["technical_summary"]


@pytest.mark.asyncio
async def test_summarize_force_refresh(async_client, auth_token, test_job_card):
    """Test force_refresh bypasses cache."""
    mock_ai_result = '{"technical_summary": "Fresh", "customer_summary": "Fresh2", "urgency": "low", "estimated_cost": 500, "recommended_action": "Wait"}'
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = mock_ai_result
        
        # First call
        await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        
        # Force refresh
        response = await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize?force_refresh=true",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["cached"] is False


@pytest.mark.asyncio
async def test_summarize_cache_invalidation_on_state_change(async_client, auth_token, test_job_card):
    """Test cache invalidates when job state changes."""
    mock_ai_result = '{"technical_summary": "T", "customer_summary": "C", "urgency": "medium", "estimated_cost": 1000, "recommended_action": "A"}'
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = mock_ai_result
        
        # First summarize
        response1 = await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response1.json()["cached"] is False
        
        # Transition state
        await async_client.patch(
            f"/api/v1/job-cards/{test_job_card['id']}/transition",
            json={"new_state": "DIAGNOSIS"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        
        # Summarize again - should regenerate
        response2 = await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response2.json()["cached"] is False


@pytest.mark.asyncio
async def test_summarize_nonexistent_job(async_client, auth_token):
    """Test 404 for nonexistent job card."""
    response = await async_client.post(
        "/api/v1/job-cards/99999/summarize",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_summarize_without_auth(async_client, test_job_card):
    """Test 401 without authentication."""
    response = await async_client.post(
        f"/api/v1/job-cards/{test_job_card['id']}/summarize",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_summarize_safety_floor(async_client, auth_token, test_job_card):
    """Test that AI cannot downgrade urgency below keyword floor."""
    # AI tries to return "low" but keyword detection finds "brake" = "high"
    mock_ai_result = '{"technical_summary": "T", "customer_summary": "C", "urgency": "low", "estimated_cost": 100, "recommended_action": "A"}'
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = mock_ai_result
        
        response = await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        
        data = response.json()
        # Job card complaint contains "brake" so urgency should be at least "high"
        assert data["urgency"] in ["high", "critical"]


@pytest.mark.asyncio
async def test_summarize_with_estimate(async_client, auth_token, test_job_card):
    """Test summarization includes estimate data when available."""
    # Create estimate first
    await async_client.post(
        f"/api/v1/job-cards/{test_job_card['id']}/estimate",
        json={
            "lines": [
                {"description": "Brake pads", "quantity": 1, "price": 2500, "tax_rate": 0.18}
            ]
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    mock_ai_result = '{"technical_summary": "T", "customer_summary": "C", "urgency": "high", "estimated_cost": 3000, "recommended_action": "A"}'
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = mock_ai_result
        
        response = await async_client.post(
            f"/api/v1/job-cards/{test_job_card['id']}/summarize",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["estimated_cost"] > 0
