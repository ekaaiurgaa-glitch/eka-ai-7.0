import uuid
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, JSON, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, TenantMixin, TimestampMixin

class Role(Base, TimestampMixin):
    __tablename__ = "roles"
    id = Column(sa.String, primary_key=True)
    name = Column(sa.String, nullable=False, unique=True)
    permissions = Column(JSON, nullable=False, default=[])
    description = Column(sa.String)

class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    id = Column(sa.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(sa.String, nullable=False)
    type = Column(sa.String, nullable=False)  # workshop, fleet, individual
    plan_id = Column(sa.String, ForeignKey("subscription_plans.id"))
    gst_number = Column(sa.String)
    city = Column(sa.String, nullable=False)
    state = Column(sa.String, nullable=False)
    tier = Column(sa.String, nullable=False, default="tier3")
    status = Column(sa.String, nullable=False, default="active")

class User(Base, TenantMixin, TimestampMixin):
    __tablename__ = "users"
    id = Column(sa.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(sa.String, unique=True, index=True, nullable=False)
    hashed_password = Column(sa.String, nullable=False)
    full_name = Column(sa.String)
    role_id = Column(sa.String, ForeignKey("roles.id"), nullable=False)
    is_active = Column(sa.Boolean, default=True)
    
    # Relationships
    role = relationship("Role")

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
