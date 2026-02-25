import pytest
import pytest_asyncio
import uuid
from unittest.mock import patch, MagicMock
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

# Disable tracing for tests
os.environ["JAEGER_ENDPOINT"] = ""

# Mock embedding function BEFORE importing app modules that use it
import app.modules.knowledge.service as knowledge_service
import asyncio
async def mock_get_embedding(text):
    return [0.1] * 768
knowledge_service.get_embedding = mock_get_embedding

from app.db.base import Base
import app.db.models
import app.subscriptions.models
import app.modules.job_cards.model
import app.modules.vehicles.model
import app.modules.invoices.model
import app.modules.catalog.model
import app.modules.operator.model
import app.modules.mg_engine.model
import app.modules.knowledge.model
import app.approvals.models
from app.db import session as db_session_module
from app.main import app
from app.core.security import create_access_token

# Use file-based SQLite for integration tests to ensure multiple connections see the same data
TEST_DATABASE_URL = "sqlite+aiosqlite:///test_integration.db"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    TestingSessionLocal = sessionmaker(expire_on_commit=False, class_=AsyncSession, bind=engine)
    
    # Patch the application's session maker to use the test engine/session
    old_session_local = db_session_module.AsyncSessionLocal
    db_session_module.AsyncSessionLocal = TestingSessionLocal
    
    with patch("app.modules.chat.service.LLMClient.complete") as mock_gen:
        mock_gen.return_value = type('obj', (object,), {'content': 'Mocked AI response', 'model_used': 'gemini-3-flash-preview'})()
        async with TestingSessionLocal() as session:
            yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    # Restore original session maker
    db_session_module.AsyncSessionLocal = old_session_local

@pytest.fixture
def test_tenant():
    return "test_tenant"

@pytest.fixture
def test_tenant_2():
    return str(uuid.uuid4())

@pytest.fixture
def auth_headers(test_tenant):
    token = create_access_token(
        data={
            "sub": "owner",
            "tenant_id": test_tenant,
            "role": "owner",
            "permissions": ["chat_access", "can_manage_vehicles", "can_manage_jobs", "can_manage_estimates", "can_create_invoice", "can_execute_operator"]
        }
    )
    return {"Authorization": f"Bearer {token}"}

class MockLLM:
    def __init__(self):
        self.response_text = "{}"
        self.confidence = 90
        self.fail = False
    
    def set_response(self, text):
        self.response_text = text
    
    def set_confidence(self, pct):
        self.confidence = pct
    
    def set_failure(self, fail=True):
        self.fail = fail

@pytest.fixture
def mock_llm():
    return MockLLM()

class FakeRedis:
    def __init__(self):
        self.data = {}
        
    async def incr(self, key):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]
        
    async def expire(self, key, time):
        pass
        
    async def set(self, key, val, ex=None):
        self.data[key] = val
        
    async def get(self, key):
        return self.data.get(key)
        
    async def delete(self, key):
        if key in self.data:
            del self.data[key]

@pytest_asyncio.fixture
async def redis_client():
    return FakeRedis()

@pytest_asyncio.fixture
async def async_client(db_session):
    from app.core.dependencies import get_db
    
    async def _get_test_db():
        yield db_session
        
    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client(async_client):
    return async_client

@pytest.fixture
def auth_token(test_tenant):
    """Generates a valid JWT for testing."""
    return create_access_token(
        data={
            "sub": "test_user",
            "tenant_id": test_tenant,
            "role": "owner",
            "permissions": ["chat_access", "can_manage_jobs", "can_manage_estimates"]
        }
    )

@pytest_asyncio.fixture
async def test_job_card(async_client, auth_token):
    """Creates a test job card and returns its data."""
    # First create a vehicle
    v_res = await async_client.post(
        "/api/v1/vehicles/",
        json={"plate_number": "MH01AB1234", "make": "Tata", "model": "Nexon", "year": 2022, "fuel_type": "petrol"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    if v_res.status_code != 201:
        # Fallback if already exists or other error
        pass
    vehicle = v_res.json()
    
    # Then create job card
    res = await async_client.post(
        "/api/v1/job-cards/",
        json={"vehicle_id": vehicle.get("id", 1), "complaint": "Brake noise"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    return res.json()
