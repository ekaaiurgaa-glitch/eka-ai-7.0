"""Notifications API Router."""
from fastapi import APIRouter, Depends
from app.core.dependencies import get_tenant_id
from app.core.notifications import notification_service, SMSRequest, EmailRequest

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/sms")
async def send_sms(
    request: SMSRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    return await notification_service.send_sms(request)

@router.post("/email")
async def send_email(
    request: EmailRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    return await notification_service.send_email(request)

@router.post("/approval-link")
async def send_approval(
    customer_email: str,
    job_no: str,
    estimate_id: int,
    tenant_id: str = Depends(get_tenant_id)
):
    return await notification_service.send_approval_link(customer_email, job_no, estimate_id)
