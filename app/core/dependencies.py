from typing import AsyncGenerator, Optional
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async DB session dependency."""
    async with AsyncSessionLocal() as session:
        yield session


def get_tenant_id(request: Request) -> str:
    """Extract tenant_id from request state (set by TenantMiddleware)."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        return "default_tenant"
    return tenant_id


async def get_redis():
    """Optional Redis client dependency. Returns None if Redis not configured."""
    from app.core.cache import get_redis_client
    return get_redis_client()
