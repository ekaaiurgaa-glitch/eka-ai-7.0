from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class FuelType(str, Enum):
    petrol = "petrol"
    diesel = "diesel"
    electric = "electric"
    hybrid = "hybrid"


class VehicleBase(BaseModel):
    plate_number: str
    make: str
    model: str
    year: int
    fuel_type: FuelType
    vin: Optional[str] = None
    owner_name: Optional[str] = None
    monthly_km: int = 1000


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    plate_number: Optional[str] = None
    owner_name: Optional[str] = None
    monthly_km: Optional[int] = None


class Vehicle(VehicleBase):
    id: int
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
