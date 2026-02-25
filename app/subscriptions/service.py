from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import date
from . import models

async def record_usage(
    db: AsyncSession, 
    tenant_id: str, 
    tokens: int = 0, 
    actions: int = 0, 
    job_cards: int = 0
):
    """
    Updates the UsageAggregate for the current billing cycle. (P1-11)
    """
    # Simple logic to find current billing cycle
    # In a real app, you'd lookup tenant_subscriptions.billing_cycle_start
    today = date.today()
    cycle_start = today.replace(day=1)
    
    stmt = select(models.UsageAggregate).where(
        models.UsageAggregate.tenant_id == tenant_id,
        models.UsageAggregate.billing_cycle_start == cycle_start
    )
    result = await db.execute(stmt)
    usage = result.scalar_one_or_none()
    
    if not usage:
        usage = models.UsageAggregate(
            tenant_id=tenant_id,
            billing_cycle_start=cycle_start,
            total_tokens_consumed=tokens,
            total_operator_actions=actions,
            total_job_cards_created=job_cards,
            last_updated=func.now()
        )
        db.add(usage)
    else:
        usage.total_tokens_consumed += tokens
        usage.total_operator_actions += actions
        usage.total_job_cards_created += job_cards
        usage.last_updated = func.now()
        
    await db.commit()


async def check_subscription_limits(db: AsyncSession, tenant_id: str, action_type: str):
    """
    P1-27: Enforces subscription limits.
    action_type can be 'tokens', 'operator_actions', 'job_cards'
    """
    today = date.today()
    cycle_start = today.replace(day=1)
    
    # 1. Get usage
    stmt = select(models.UsageAggregate).where(
        models.UsageAggregate.tenant_id == tenant_id,
        models.UsageAggregate.billing_cycle_start == cycle_start
    )
    result = await db.execute(stmt)
    usage = result.scalar_one_or_none()
    if not usage: return # No usage yet, definitely okay
    
    # 2. Get plan limits (via tenant_subscription)
    from .models import TenantSubscription, SubscriptionPlan
    stmt = (
        select(SubscriptionPlan)
        .join(TenantSubscription, TenantSubscription.plan_id == SubscriptionPlan.id)
        .where(TenantSubscription.tenant_id == tenant_id)
    )
    result = await db.execute(stmt)
    plan = result.scalar_one_or_none()
    if not plan: return # default/trial?
    
    # 3. Compare
    from fastapi import HTTPException
    if action_type == 'tokens' and plan.token_limit and usage.total_tokens_consumed >= plan.token_limit:
        raise HTTPException(status_code=402, detail="SUBSCRIPTION_LIMIT_EXCEEDED: Token limit reached for this month.")
    if action_type == 'operator_actions' and plan.operator_actions_per_day:
        # Simplified: checking aggregate for now
        if usage.total_operator_actions >= (plan.operator_actions_per_day * 30):
             raise HTTPException(status_code=402, detail="SUBSCRIPTION_LIMIT_EXCEEDED: Operator actions limit reached.")
    if action_type == 'job_cards' and plan.job_card_limit_per_month and usage.total_job_cards_created >= plan.job_card_limit_per_month:
        raise HTTPException(status_code=402, detail="SUBSCRIPTION_LIMIT_EXCEEDED: Job card limit reached for this month.")
