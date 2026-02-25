from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class JobCardCreate(BaseModel):
    vehicle_id: int
    complaint: str


class JobCardResponse(BaseModel):
    id: int
    job_no: str
    vehicle_id: int
    complaint: str
    state: str
    tenant_id: str
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EstimateLine(BaseModel):
    part_id: Optional[int] = None
    description: Optional[str] = None
    quantity: int
    price: float
    tax_rate: float = 0.18  # Default GST


class EstimateCreate(BaseModel):
    lines: List[EstimateLine]


class Estimate(BaseModel):
    id: int
    job_id: int
    lines: list[EstimateLine]
    total_parts: float
    total_labor: float
    tax_breakdown: dict
    tenant_id: str

    model_config = ConfigDict(from_attributes=True)


class EstimateResponse(BaseModel):
    id: int
    job_id: int
    lines: list
    total_parts: float
    total_labor: float
    tax_breakdown: dict
    tenant_id: str

    model_config = ConfigDict(from_attributes=True)


class StateTransition(BaseModel):
    new_state: str


class SummarizeResponse(BaseModel):
    """AI-generated summary of job card for customer communication."""
    job_id: int
    job_no: str
    technical_summary: str
    customer_summary: str
    urgency: str  # low, medium, high, critical
    estimated_cost: float
    recommended_action: str
    cached: bool = False
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
