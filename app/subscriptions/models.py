from sqlalchemy import Column, String, Integer, BigInteger, Numeric, Boolean, Date, DateTime, JSON, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.db.base import Base, TenantMixin, TimestampMixin


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(String, primary_key=True)
    plan_name = Column(String, nullable=False, unique=True)
    monthly_price_inr = Column(Numeric(10, 2), nullable=False)
    token_limit = Column(BigInteger, nullable=True)
    operator_actions_per_day = Column(Integer, nullable=True)
    job_card_limit_per_month = Column(Integer, nullable=True)
    api_requests_per_minute = Column(Integer, nullable=False, default=20)
    enforcement_policy = Column(String, nullable=False)
    overage_rate_per_1k_tokens = Column(Numeric(8, 4), nullable=True)
    features = Column(JSON, nullable=False, default={})
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint("enforcement_policy IN ('hard_stop','soft_limit','overage_billing','grace_period')"),
    )


class TenantSubscription(Base, TenantMixin, TimestampMixin):
    __tablename__ = "tenant_subscriptions"
    
    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey("subscription_plans.id"), nullable=False)
    status = Column(String, nullable=False, default="active")
    billing_cycle_start = Column(Date, nullable=False)
    billing_cycle_end = Column(Date, nullable=False)
    auto_renew = Column(Boolean, nullable=False, default=True)
    payment_method_ref = Column(String, nullable=True)
    grace_period_ends_at = Column(DateTime, nullable=True)
    
    plan = relationship("SubscriptionPlan")
    
    __table_args__ = (
        CheckConstraint("status IN ('active','expired','suspended','cancelled','grace_period')"),
    )


class UsageAggregate(Base):
    __tablename__ = "usage_aggregates"
    
    tenant_id = Column(String, nullable=False, primary_key=True)
    billing_cycle_start = Column(Date, nullable=False, primary_key=True)
    total_tokens_consumed = Column(BigInteger, nullable=False, default=0)
    total_operator_actions = Column(Integer, nullable=False, default=0)
    total_job_cards_created = Column(Integer, nullable=False, default=0)
    total_mg_calculations = Column(Integer, nullable=False, default=0)
    total_storage_bytes = Column(BigInteger, nullable=False, default=0)
    total_api_requests = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=func.now())


class OverageLedger(Base, TenantMixin, TimestampMixin):
    __tablename__ = "overage_ledger"
    
    id = Column(String, primary_key=True)
    billing_cycle = Column(Date, nullable=False)
    overage_type = Column(String, nullable=False)
    overage_units = Column(BigInteger, nullable=False)
    rate_per_unit = Column(Numeric(10, 6), nullable=False)
    amount_inr = Column(Numeric(10, 2), nullable=False)
    billed = Column(Boolean, nullable=False, default=False)
