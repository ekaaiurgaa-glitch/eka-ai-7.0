from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from app.db.base import Base, TenantMixin, TimestampMixin


class AuditLog(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)
    entity_id = Column(String, index=True)  # Fixed: was Integer; Operator uses UUID strings
    actor_id = Column(String)
    action = Column(String)
    payload = Column(JSON)

# Other shared models can be defined here.
