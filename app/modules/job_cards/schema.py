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
    part_id: int
    quantity: int
    price: float
    tax_rate: float

class EstimateBase(BaseModel):
    job_id: int
    lines: list[EstimateLine]

class EstimateCreate(EstimateBase):
    pass

class Estimate(EstimateBase):
    id: int
    total_parts: float
    total_labor: float
    tax_breakdown: dict

    model_config = {"from_attributes": True}
