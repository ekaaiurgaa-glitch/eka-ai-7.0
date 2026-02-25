from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.dependencies import get_db, get_tenant_id
from app.core.rbac import require_role
from app.subscriptions import models, schema

router = APIRouter(prefix="/v1/subscriptions", tags=["subscriptions"])

@router.get("/plans", response_model=List[schema.SubscriptionPlan])
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.SubscriptionPlan).where(models.SubscriptionPlan.is_active == True))
    return result.scalars().all()

@router.get("/my-subscription", response_model=schema.TenantSubscription)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["owner", "manager"]))
):
    result = await db.execute(
        select(models.TenantSubscription)
        .where(models.TenantSubscription.tenant_id == tenant_id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@router.get("/usage", response_model=schema.UsageAggregate)
async def get_my_usage(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["owner", "manager"]))
):
    result = await db.execute(
        select(models.UsageAggregate)
        .where(models.UsageAggregate.tenant_id == tenant_id)
        .order_by(models.UsageAggregate.billing_cycle_start.desc())
    )
    usage = result.first()
    if not usage:
        raise HTTPException(status_code=404, detail="Usage data not found")
    return usage
