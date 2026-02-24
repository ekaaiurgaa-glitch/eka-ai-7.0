from sqlalchemy import Column, Integer, String, JSON, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base, TenantMixin, TimestampMixin

class Invoice(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobcard.id"))
    lines = Column(JSON)
    total_amount = Column(Float)
    tax_amount = Column(Float)

    # Relationship to JobCard (assuming one-to-one or one-to-many)
    job_card = relationship("JobCard")
