from pydantic import BaseModel
from typing import Optional, List

class VehicleContext(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    fuel: Optional[str] = None

class ChatQueryRequest(BaseModel):
    query: str
    vehicle: Optional[VehicleContext] = None
    tenant_id: Optional[str] = None

class ChatQueryResponse(BaseModel):
    issue_summary: str
    probable_causes: List[str]
    diagnostic_steps: List[str]
    safety_advisory: str
    confidence_level: float
    rag_references: Optional[List[str]] = None
    tokens_used: Optional[int] = None
