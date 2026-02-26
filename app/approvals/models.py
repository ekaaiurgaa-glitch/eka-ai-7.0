import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from app.db.base import Base, TenantMixin, TimestampMixin
import uuid

class CustomerApproval(Base, TenantMixin, TimestampMixin):
    __tablename__ = "customer_approvals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_card_id = Column(String, nullable=False)
    estimate_id = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    approval_token = Column(String, unique=True, nullable=False)
    token_expires_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending", nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    e_signature_ref = Column(String, nullable=True)
    notification_sent_at = Column(DateTime(timezone=True), nullable=True)

class ApprovalRule(Base, TenantMixin, TimestampMixin):
    __tablename__ = "approval_rules"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_name = Column(String, nullable=False)
    rule_type = Column(String, default="estimate_value") # estimate_value, etc
    threshold_value = Column(String, nullable=True) # e.g. "10000"
    is_active = Column(Boolean, default=True)

    def trigger_approval(self, value):
        if self.rule_type == "estimate_value" and value:
            try:
                return float(value) > float(self.threshold_value)
            except (ValueError, TypeError):
                return False
        return False


