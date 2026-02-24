from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TenantMixin, TimestampMixin


class JobCard(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    job_no = Column(String, unique=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id"), index=True)
    complaint = Column(String)
    state = Column(String, default="OPEN")
    created_by = Column(String)  # User ID

    # Relationships
    estimates = relationship("Estimate", back_populates="job_card")


class Estimate(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobcard.id"))
    lines = Column(JSON)
    total_parts = Column(Float)
    total_labor = Column(Float)
    tax_breakdown = Column(JSON)
    approved = Column(Boolean, default=False)  # Fixed: was missing, caused AttributeError in service

    # Relationships
    job_card = relationship("JobCard", back_populates="estimates")


class JobSummary(Base, TenantMixin, TimestampMixin):
    """Cache for AI-generated job card summaries."""
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobcard.id"), unique=True, index=True)
    job_state_at_summary = Column(String)  # Invalidate cache when job state changes
    
    # Summary fields
    technical_summary = Column(String)
    customer_summary = Column(String)
    urgency = Column(String)  # low, medium, high, critical
    estimated_cost = Column(Float)
    recommended_action = Column(String)
    
    # Metadata
    generated_at = Column(DateTime)
    force_refresh = Column(Boolean, default=False)
