import uuid
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from app.db.base import Base, TenantMixin, TimestampMixin

class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    id = Column(sa.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(sa.String, nullable=False)
    type = Column(sa.String, nullable=False)  # workshop, fleet, individual
    plan_id = Column(sa.String)
    gst_number = Column(sa.String)
    city = Column(sa.String, nullable=False)
    state = Column(sa.String, nullable=False) # Added for GST supply logic
    tier = Column(sa.String, nullable=False, default="tier3")
    status = Column(sa.String, nullable=False, default="active")

class AuditLog(Base, TenantMixin, TimestampMixin):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)
    entity_id = Column(String, index=True)
    actor_id = Column(String)
    action = Column(String)
    payload = Column(JSON)
    old_state = Column(JSON)
    new_state = Column(JSON)
