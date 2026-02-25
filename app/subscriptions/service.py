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
