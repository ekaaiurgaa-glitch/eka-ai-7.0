from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from app.db.base import Base, TenantMixin, TimestampMixin
import uuid
from sqlalchemy import func

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
