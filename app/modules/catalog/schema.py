from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PartBase(BaseModel):
    part_number: str
    description: str
    hsn_code: str
    unit_price: float
    gst_rate: float = 18.0


class PartCreate(PartBase):
    pass


class Part(PartBase):
    id: int
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LaborRateBase(BaseModel):
    service_type: str
    city: str = "default"
    rate_per_hour: float
    estimated_hours: float = 1.0


class LaborRateCreate(LaborRateBase):
    pass


class LaborRate(LaborRateBase):
    id: int
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
