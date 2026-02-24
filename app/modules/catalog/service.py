from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from . import model, schema
from app.core.cache import cache_get, cache_set


async def get_part(db: AsyncSession, part_id: int, tenant_id: str) -> model.Part:
    cache_key = f"part:{tenant_id}:{part_id}"
    cached = cache_get(cache_key)
    if cached:
        # Return dict instead of detached instance to avoid SQLAlchemy session issues
        # Caller should handle dict or re-query if session operations needed
        return cached

    result = await db.execute(
        select(model.Part).filter(model.Part.id == part_id, model.Part.tenant_id == tenant_id)
    )
    part = result.scalar_one_or_none()
    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found in catalog")
    cache_set(cache_key, {c.name: getattr(part, c.name) for c in part.__table__.columns}, ttl=3600)
    return part


async def list_parts(db: AsyncSession, tenant_id: str) -> List[model.Part]:
    result = await db.execute(
        select(model.Part).filter(model.Part.tenant_id == tenant_id)
    )
    return result.scalars().all()


async def get_labor_rate(db: AsyncSession, service_type: str, city: str, tenant_id: str) -> Optional[model.LaborRate]:
    """Lookup labor rate by service_type + city; falls back to 'default' city."""
    cache_key = f"labor:{tenant_id}:{service_type}:{city}"
    cached = cache_get(cache_key)
    if cached:
        # Return dict instead of detached instance
        return cached

    result = await db.execute(
        select(model.LaborRate).filter(
            model.LaborRate.service_type == service_type,
            model.LaborRate.city == city,
            model.LaborRate.tenant_id == tenant_id,
        )
    )
    rate = result.scalar_one_or_none()
    if not rate:
        # Fall back to 'default' city rate
        result = await db.execute(
            select(model.LaborRate).filter(
                model.LaborRate.service_type == service_type,
                model.LaborRate.city == "default",
                model.LaborRate.tenant_id == tenant_id,
            )
        )
        rate = result.scalar_one_or_none()
    if rate:
        cache_set(cache_key, {c.name: getattr(rate, c.name) for c in rate.__table__.columns}, ttl=3600)
    return rate


async def create_part(db: AsyncSession, part: schema.PartCreate, tenant_id: str) -> model.Part:
    db_part = model.Part(**part.model_dump(), tenant_id=tenant_id)
    db.add(db_part)
    await db.commit()
    await db.refresh(db_part)
    return db_part


async def create_labor_rate(db: AsyncSession, rate: schema.LaborRateCreate, tenant_id: str) -> model.LaborRate:
    db_rate = model.LaborRate(**rate.model_dump(), tenant_id=tenant_id)
    db.add(db_rate)
    await db.commit()
    await db.refresh(db_rate)
    return db_rate
