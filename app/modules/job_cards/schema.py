from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCardBase(BaseModel):
    vehicle_id: int
    complaint: str
    state: str = "OPEN"

class JobCardCreate(JobCardBase):
    pass

class JobCard(JobCardBase):
    id: int
    tenant_id: str
    job_no: str
    created_at: datetime
    created_by: str

    model_config = {"from_attributes": True}

class EstimateLine(BaseModel):
    part_id: Optional[int] = None
    description: Optional[str] = None
    quantity: int
    price: float
    tax_rate: float = 0.18  # Default GST

class EstimateBase(BaseModel):
    lines: list[EstimateLine]

class EstimateCreate(EstimateBase):
    pass

class Estimate(BaseModel):
    id: int
    job_id: int
    lines: list[EstimateLine]
    total_parts: float
    total_labor: float
    tax_breakdown: dict

    model_config = {"from_attributes": True}
