"""Integration tests for job card summarize endpoint."""
import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_summarize_endpoint_creates_summary(client, auth_headers, db_session):
    """Test that summarize endpoint creates and returns AI summary."""
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema
    
    # Create vehicle and job card
    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(
            plate_number="SUM001",
            make="Maruti",
            model="Swift",
            year=2019,
            fuel_type=v_schema.FuelType.petrol,
        ),
        "test_tenant",
    )
    
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Brake noise when stopping"),
        "test_tenant",
        "test_user",
    )
    
    # Mock Gemini to avoid API call
    mock_response = '''{
        "technical_summary": "Brake pads worn to 2mm",
        "customer_summary": "Your brake pads are thin and need replacement soon.",
        "urgency": "high",
        "estimated_cost": 3500,
        "recommended_action": "Schedule brake service within 1 week"
    }'''
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock, return_value=mock_response):
        response = await client.post(
            f"/api/v1/job-cards/{job.id}/summarize",
            headers=auth_headers,
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["job_id"] == job.id
    assert data["job_no"] == job.job_no
    assert "technical_summary" in data
    assert "customer_summary" in data
    assert data["urgency"] == "high"  # Safety floor from brake keyword
    assert data["cached"] == False


@pytest.mark.asyncio
async def test_summarize_endpoint_returns_cached_on_second_call(client, auth_headers, db_session):
    """Test that second call returns cached summary."""
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema
    
    # Create vehicle and job card
    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="SUM002", make="Honda", model="City", year=2020),
        "test_tenant",
    )
    
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Oil change due"),
        "test_tenant",
        "test_user",
    )
    
    mock_response = '''{
        "technical_summary": "Oil change needed",
        "customer_summary": "Regular maintenance due.",
        "urgency": "low",
        "estimated_cost": 1500,
        "recommended_action": "Schedule at convenience"
    }'''
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock, return_value=mock_response):
        # First call - generates and caches
        response1 = await client.post(
            f"/api/v1/job-cards/{job.id}/summarize",
            headers=auth_headers,
        )
        assert response1.status_code == 200
        assert response1.json()["cached"] == False
        
        # Second call - returns cached
        response2 = await client.post(
            f"/api/v1/job-cards/{job.id}/summarize",
            headers=auth_headers,
        )
        assert response2.status_code == 200
        assert response2.json()["cached"] == True
        
        # Same content
        assert response1.json()["technical_summary"] == response2.json()["technical_summary"]


@pytest.mark.asyncio
async def test_summarize_endpoint_force_refresh_bypasses_cache(client, auth_headers, db_session):
    """Test that force_refresh=true bypasses cache."""
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema
    
    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="SUM003", make="Tata", model="Nexon", year=2021),
        "test_tenant",
    )
    
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="Tire rotation needed"),
        "test_tenant",
        "test_user",
    )
    
    mock_response = '''{
        "technical_summary": "Tire rotation",
        "customer_summary": "Rotate tires for even wear.",
        "urgency": "low",
        "estimated_cost": 800,
        "recommended_action": "Schedule with next service"
    }'''
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock, return_value=mock_response):
        # First call - cached
        await client.post(
            f"/api/v1/job-cards/{job.id}/summarize",
            headers=auth_headers,
        )
        
        # Second call with force_refresh - should regenerate
        response = await client.post(
            f"/api/v1/job-cards/{job.id}/summarize?force_refresh=true",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        assert response.json()["cached"] == False  # Fresh generation


@pytest.mark.asyncio
async def test_summarize_endpoint_invalidates_cache_on_state_change(client, auth_headers, db_session):
    """Test that cache invalidates when job card state changes."""
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema
    
    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="SUM004", make="Toyota", model="Innova", year=2018),
        "test_tenant",
    )
    
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="AC not cooling"),
        "test_tenant",
        "test_user",
    )
    
    mock_response = '''{
        "technical_summary": "AC inspection needed",
        "customer_summary": "Air conditioning requires service.",
        "urgency": "medium",
        "estimated_cost": 2500,
        "recommended_action": "Schedule AC service"
    }'''
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock, return_value=mock_response):
        # Generate summary in OPEN state
        response1 = await client.post(
            f"/api/v1/job-cards/{job.id}/summarize",
            headers=auth_headers,
        )
        assert response1.json()["cached"] == False
        
        # Transition job to DIAGNOSIS state
        await client.patch(
            f"/api/v1/job-cards/{job.id}/transition",
            json={"new_state": "DIAGNOSIS"},
            headers=auth_headers,
        )
        
        # Summary should regenerate (state changed)
        response2 = await client.post(
            f"/api/v1/job-cards/{job.id}/summarize",
            headers=auth_headers,
        )
        assert response2.json()["cached"] == False  # Cache invalidated by state change


@pytest.mark.asyncio
async def test_summarize_endpoint_job_not_found(client, auth_headers):
    """Test 404 for non-existent job card."""
    response = await client.post(
        "/api/v1/job-cards/99999/summarize",
        headers=auth_headers,
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_summarize_endpoint_safety_floor_enforced(client, auth_headers, db_session):
    """Test that safety floor prevents AI from downgrading urgency."""
    from app.modules.vehicles import service as v_service, schema as v_schema
    from app.modules.job_cards import service as j_service, schema as j_schema
    
    vehicle = await v_service.create_vehicle(
        db_session,
        v_schema.VehicleCreate(plate_number="SUM005", make="BMW", model="X5", year=2020),
        "test_tenant",
    )
    
    # Brake failure = critical keyword
    job = await j_service.create_job_card(
        db_session,
        j_schema.JobCardCreate(vehicle_id=vehicle.id, complaint="brake failure reported by customer"),
        "test_tenant",
        "test_user",
    )
    
    # AI tries to say "low" urgency (simulating bad model output)
    mock_response = '''{
        "technical_summary": "Brake issue",
        "customer_summary": "Minor brake adjustment needed.",
        "urgency": "low",
        "estimated_cost": 500,
        "recommended_action": "Schedule when convenient"
    }'''
    
    with patch("app.ai.summarization.call_gemini", new_callable=AsyncMock, return_value=mock_response):
        response = await client.post(
            f"/api/v1/job-cards/{job.id}/summarize",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Safety floor: brake failure keyword = critical/high
        # AI suggested "low" but should be overridden
        assert data["urgency"] in ["critical", "high"]
        assert data["urgency"] != "low"  # Safety floor prevented downgrade
