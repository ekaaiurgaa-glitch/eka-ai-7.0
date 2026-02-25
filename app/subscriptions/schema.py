from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date

class SubscriptionPlan(BaseModel):
    id: str
    plan_name: str
    monthly_price_inr: float
    token_limit: Optional[int]
    operator_actions_per_day: Optional[int]
    job_card_limit_per_month: Optional[int]
    api_requests_per_minute: int
    enforcement_policy: str
    features: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)

class TenantSubscription(BaseModel):
    id: str
    plan_id: str
    status: str
    billing_cycle_start: date
    billing_cycle_end: date
    auto_renew: bool
    
    model_config = ConfigDict(from_attributes=True)

class UsageAggregate(BaseModel):
    tenant_id: str
    billing_cycle_start: date
    total_tokens_consumed: int
    total_operator_actions: int
    total_job_cards_created: int
    total_api_requests: int
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)
