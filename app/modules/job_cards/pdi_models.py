from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TenantMixin, TimestampMixin

class PDIRecord(Base, TenantMixin, TimestampMixin):
    __tablename__ = "pdi_records"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    job_card_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    checklist = Column(JSON, nullable=False)
    overall_passed = Column(Boolean, nullable=False)
    inspector_id = Column(UUID(as_uuid=True), nullable=False)
    photos = Column(JSON, server_default='[]', nullable=False)
    inspected_at = Column(DateTime(timezone=True), nullable=False)
