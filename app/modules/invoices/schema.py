from pydantic import BaseModel
from typing import List
from datetime import datetime

class InvoiceLine(BaseModel):
    part_id: int
    quantity: int
    price: float
    tax_rate: float
    hsn_code: str

class InvoiceBase(BaseModel):
    job_id: int
    lines: List[InvoiceLine]

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    tenant_id: str
    total_amount: float
    tax_amount: float
    created_at: datetime

    model_config = {"from_attributes": True}
