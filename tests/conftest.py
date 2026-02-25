import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

# Assuming an SQLite test db for simplicity
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    TestingSessionLocal = sessionmaker(expire_on_commit=False, class_=AsyncSession, bind=engine)
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def test_tenant():
    return str(uuid.uuid4())

@pytest.fixture
def test_tenant_2():
    return str(uuid.uuid4())

@pytest.fixture
def auth_headers(test_tenant):
    return {
        "owner": {"Authorization": f"Bearer mock_token_owner_{test_tenant}"},
        "manager": {"Authorization": f"Bearer mock_token_manager_{test_tenant}"},
        "technician": {"Authorization": f"Bearer mock_token_tech_{test_tenant}"},
        "customer": {"Authorization": f"Bearer mock_token_customer_{test_tenant}"}
    }

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
