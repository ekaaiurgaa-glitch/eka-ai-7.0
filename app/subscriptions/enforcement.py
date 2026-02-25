from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.subscriptions.models import TenantSubscription, SubscriptionPlan, UsageAggregate
from app.core.cache import cache_get, cache_set
import json


@dataclass
class EnforcementResult:
    allowed: bool
    warning: Optional[str] = None
    error_code: Optional[str] = None
    retry_after_seconds: Optional[int] = None


class SubscriptionEnforcer:
    def __init__(self, db: AsyncSession, redis_client):
        self.db = db
        self.redis = redis_client
    
    async def check(self, tenant_id: str, action_type: str, tokens_estimate: int = 0) -> EnforcementResult:
        """
        Enforce subscription limits with policy-based decisions.
        
        Decision matrix:
        1. Fetch tenant subscription + plan limits
        2. Check subscription status
        3. Check Redis rate limit (requests per minute)
        4. Check monthly aggregate vs plan limits
        5. Apply enforcement policy
        6. Return result
        """
        # 1. Fetch subscription
        result = await self.db.execute(
            select(TenantSubscription, SubscriptionPlan)
            .join(SubscriptionPlan)
            .where(TenantSubscription.tenant_id == tenant_id)
        )
        row = result.first()
        
        if not row:
            return EnforcementResult(
                allowed=False,
                error_code="NO_SUBSCRIPTION",
                warning="No active subscription found"
            )
        
        subscription, plan = row
        
        # 2. Check subscription status
        if subscription.status not in ('active', 'grace_period'):
            return EnforcementResult(
                allowed=False,
                error_code="SUBSCRIPTION_INACTIVE",
                warning=f"Subscription status: {subscription.status}"
            )
        
        # 3. Check rate limit (Redis)
        rate_limit_key = f"rate_limit:{tenant_id}:minute"
        current_count = await self._check_rate_limit(rate_limit_key, plan.api_requests_per_minute)
        
        if current_count > plan.api_requests_per_minute:
            return EnforcementResult(
                allowed=False,
                error_code="RATE_LIMIT_EXCEEDED",
                retry_after_seconds=60
            )
        
        # 4. Check monthly limits
        billing_start = subscription.billing_cycle_start
        usage_result = await self.db.execute(
            select(UsageAggregate).where(
                UsageAggregate.tenant_id == tenant_id,
                UsageAggregate.billing_cycle_start == billing_start
            )
        )
        usage = usage_result.scalar_one_or_none()
        
        if not usage:
            # No usage yet this cycle - allow
            return EnforcementResult(allowed=True)
        
        # 5. Apply enforcement policy
        return await self._apply_policy(plan, usage, tokens_estimate, action_type)
    
    async def _check_rate_limit(self, key: str, limit: int) -> int:
        """Increment Redis counter with 60s TTL"""
        if not self.redis:
            return 0
        
        try:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, 60)
            return count
        except:
            return 0
    
    async def _apply_policy(self, plan: SubscriptionPlan, usage: UsageAggregate, 
                           tokens_estimate: int, action_type: str) -> EnforcementResult:
        """Apply enforcement policy based on plan type"""
        policy = plan.enforcement_policy
        
        # Check token limit
        if plan.token_limit:
            usage_pct = (usage.total_tokens_consumed / plan.token_limit) * 100
            
            if policy == "hard_stop":
                if usage.total_tokens_consumed >= plan.token_limit:
                    return EnforcementResult(
                        allowed=False,
                        error_code="TOKEN_LIMIT_EXCEEDED",
                        warning=f"Token limit reached: {usage.total_tokens_consumed}/{plan.token_limit}"
                    )
            
            elif policy == "soft_limit":
                if usage_pct >= 110:
                    return EnforcementResult(
                        allowed=False,
                        error_code="SOFT_LIMIT_EXCEEDED",
                        warning=f"Soft limit exceeded: {usage_pct:.1f}%"
                    )
                elif usage_pct >= 90:
                    return EnforcementResult(
                        allowed=True,
                        warning=f"Approaching limit: {usage_pct:.1f}% used"
                    )
            
            elif policy == "overage_billing":
                # Always allow, record overage
                if usage.total_tokens_consumed > plan.token_limit:
                    return EnforcementResult(
                        allowed=True,
                        warning=f"Overage billing active: {usage.total_tokens_consumed - plan.token_limit} tokens over"
                    )
            
            elif policy == "grace_period":
                # Always allow during grace period
                return EnforcementResult(
                    allowed=True,
                    warning="Grace period active"
                )
        
        # Check action limits
        if action_type == "operator_action" and plan.operator_actions_per_day:
            if usage.total_operator_actions >= plan.operator_actions_per_day:
                return EnforcementResult(
                    allowed=False,
                    error_code="DAILY_ACTION_LIMIT_EXCEEDED"
                )
        
        if action_type == "job_card_create" and plan.job_card_limit_per_month:
            if usage.total_job_cards_created >= plan.job_card_limit_per_month:
                return EnforcementResult(
                    allowed=False,
                    error_code="MONTHLY_JOB_CARD_LIMIT_EXCEEDED"
                )
        
        return EnforcementResult(allowed=True)
