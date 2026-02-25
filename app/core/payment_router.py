"""Payment Gateway API Router."""
from fastapi import APIRouter, Depends
from app.core.dependencies import get_tenant_id
from app.core.payment_gateway import gateway, PaymentRequest

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create")
async def create_payment(
    request: PaymentRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    return await gateway.create_payment(request)

@router.get("/verify/{payment_id}")
async def verify_payment(
    payment_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    return await gateway.verify_payment(payment_id)
