from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from app.db.base import Base, TenantMixin, TimestampMixin

class OperatorPreview(Base, TenantMixin, TimestampMixin):
    __tablename__ = "operator_previews"
    id = Column(String, primary_key=True, index=True) # Using UUID as string
    actor_id = Column(String)
    tool_name = Column(String)
    args_json = Column(JSON)
    preview_json = Column(JSON)
    expires_at = Column(DateTime)

class OperatorExecution(Base, TenantMixin, TimestampMixin):
    __tablename__ = "operator_executions"
    id = Column(Integer, primary_key=True, index=True)
    preview_id = Column(String, ForeignKey("operator_previews.id"))
    execution_result = Column(JSON)
    status = Column(String) # success, error
