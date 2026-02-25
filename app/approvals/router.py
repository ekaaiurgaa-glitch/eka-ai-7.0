from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.core.dependencies import get_db, get_tenant_id
from app.core.rbac import require_role
from app.approvals.service import send_approval_request, process_approval_response

router = APIRouter(prefix="/approvals", tags=["Approvals"])

class ApprovalResponseRequest(BaseModel):
    decision: str
    signature_ref: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

@router.post("/send")
async def send_approval(
    job_card_id: UUID,
    estimate_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["manager", "owner"]))
):
    """
    sends approval request to customer (role: manager/owner)
    """
    approval = await send_approval_request(db, job_card_id, estimate_id, tenant_id)
    return {"status": "success", "approval_token": approval.approval_token}

@router.get("/{token}/review")
async def review_estimate(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    public endpoint — returns estimate summary for customer review
    """
    return {"status": "success", "estimate_summary": "Dummy estimate summary data"}

@router.post("/{token}/respond")
async def respond_to_approval(
    token: str,
    request: Request,
    response_req: ApprovalResponseRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    public endpoint — customer submits decision
    """
    ip = request.client.host if request.client else "0.0.0.0"
    approval = await process_approval_response(
        db, 
        token, 
        response_req.decision, 
        ip, 
        response_req.signature_ref
    )
    return {"status": "success", "decision": approval.status}

@router.get("/status/{job_card_id}")
async def get_approval_status(
    job_card_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["manager", "owner", "technician"]))
):
    """
    returns current approval status
    """
    return {"status": "pending_implementation"}
