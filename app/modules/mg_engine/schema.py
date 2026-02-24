from pydantic import BaseModel, Field
from enum import Enum

class FuelType(str, Enum):
    petrol = "petrol"
    diesel = "diesel"
    electric = "electric"
    hybrid = "hybrid"

class WarrantyStatus(str, Enum):
    under_warranty = "under_warranty"
    out_of_warranty = "out_of_warranty"

class UsageType(str, Enum):
    personal = "personal"
    commercial = "commercial"

class MGCalculationRequest(BaseModel):
    make: str
    model: str
    year: int
    fuel_type: FuelType
    city: str
    monthly_km: int = Field(..., gt=0)
    warranty_status: WarrantyStatus
    usage_type: UsageType
    tenant_id: Optional[str] = None

class MGCalculationResponse(BaseModel):
    annual_parts: float
    annual_labor: float
    city_adj: float
    risk_adj: float
    final_annual_cost: float
    monthly_mg: float
    notes: str
