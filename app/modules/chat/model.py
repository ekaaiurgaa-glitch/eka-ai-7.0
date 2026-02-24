from sqlalchemy import Column, Integer, String, JSON, Float, Text
from app.db.base import Base, TenantMixin, TimestampMixin

class ChatRequest(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    query_hash = Column(String, index=True)
    vehicle_json = Column(JSON)
    response_json = Column(JSON)
    confidence = Column(Float)
    rag_refs = Column(JSON)
    query_text = Column(Text)
