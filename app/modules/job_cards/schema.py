from pydantic import BaseModel
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

    class Config:
        from_attributes = True


class EstimateLine(BaseModel):
<<<<<<< HEAD
    part_id: Optional[int] = None
    description: Optional[str] = None
    quantity: int
    price: float
    tax_rate: float = 0.18  # Default GST

class EstimateBase(BaseModel):
    lines: list[EstimateLine]
=======
    description: str
    quantity: int
    price: float
    tax_rate: float = 0.18

>>>>>>> 091bcd42a89e389383604168e2df6463590a094c

class EstimateCreate(BaseModel):
    lines: List[EstimateLine]

<<<<<<< HEAD
class Estimate(BaseModel):
    id: int
    job_id: int
    lines: list[EstimateLine]
=======

class Estimate(BaseModel):
    id: int
    job_id: int
    lines: list
>>>>>>> 091bcd42a89e389383604168e2df6463590a094c
    total_parts: float
    total_labor: float
    tax_breakdown: dict
    tenant_id: str

    class Config:
        from_attributes = True


class EstimateResponse(BaseModel):
    id: int
    job_id: int
    lines: list
    total_parts: float
    total_labor: float
    tax_breakdown: dict
    tenant_id: str

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True
