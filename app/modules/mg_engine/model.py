from sqlalchemy import Column, Integer, String, JSON, Float
from app.db.base import Base, TenantMixin, TimestampMixin

class MGProposal(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, index=True) # Assuming a Vehicle model exists
    proposal_json = Column(JSON)
    monthly_mg = Column(Float)
