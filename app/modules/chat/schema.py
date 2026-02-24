from pydantic import BaseModel
from typing import Optional

class VehicleContext(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    fuel: Optional[str] = None

class ChatQueryRequest(BaseModel):
    query: str
    vehicle: Optional[VehicleContext]
    tenant_id: str

class ChatQueryResponse(BaseModel):
    issue_summary: str
    probable_causes: list[str]
    diagnostic_steps: list[str]
    safety_advisory: str
    confidence_level: float
    rag_references: Optional[list[str]] = None
