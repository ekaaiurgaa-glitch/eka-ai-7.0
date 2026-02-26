from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.core.dependencies import get_db, get_tenant_id
from app.core.rbac import require_role
from app.approvals.service import send_approval_request, process_approval_response
from sqlalchemy import select
import sqlalchemy as sa

from app.approvals.models import CustomerApproval

router = APIRouter(prefix="/approvals", tags=["Approvals"])

@router.get("")
async def list_approvals(db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id), _: dict = Depends(require_role(["owner", "manager"]))):
    result = await db.execute(select(CustomerApproval).where(CustomerApproval.tenant_id == tenant_id))
    approvals = result.scalars().all()
    
    formatted = []
    for a in approvals:
        formatted.append({
            "id": a.id,
            "token": a.approval_token,
            "type": "estimate_approval",
            "title": f"Estimate Approval for Job: {a.job_card_id}",
            "requester": "System",
            "description": f"Customer approval for estimate {a.estimate_id} on job {a.job_card_id}",
            "requested_at": a.created_at.isoformat() if hasattr(a, "created_at") and getattr(a, "created_at", None) else None,
            "urgency": "normal",
            "status": a.status,
            "resolved_at": a.approved_at.isoformat() if a.approved_at else None,
            "resolved_by": "Customer" if a.status != "pending" else None,
            "rejection_reason": a.rejection_reason,
            "data": {
                "job_no": a.job_card_id,
                "estimate_id": a.estimate_id,
                "customer_id": a.customer_id
            }
        })
    return formatted

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

@router.get("/rules")
async def get_rules(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["manager", "owner"]))
):
    from app.approvals.service import list_approval_rules
    return await list_approval_rules(db, tenant_id)

class RuleCreate(BaseModel):
    name: str
    threshold: str

@router.post("/rules")
async def create_rule(
    rule_in: RuleCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_role(["owner"]))
):
    from app.approvals.service import create_approval_rule
    return await create_approval_rule(db, rule_in.name, rule_in.threshold, tenant_id)

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
    result = await db.execute(select(CustomerApproval).where(
        sa.and_(
            CustomerApproval.job_card_id == str(job_card_id),
            CustomerApproval.tenant_id == tenant_id
        )
    ))
    approval = result.scalar_one_or_none()
    if not approval:
        return {"status": "none"}
    return {"status": approval.status, "id": approval.id}
