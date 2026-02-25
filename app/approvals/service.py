import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException
from app.approvals.models import CustomerApproval

async def send_approval_request(db: AsyncSession, job_card_id: UUID, estimate_id: UUID, tenant_id: UUID) -> CustomerApproval:
    """
    1. Generate cryptographically secure approval_token
    2. Set token_expires_at = now() + 24 hours
    3. Insert CustomerApproval record with status='pending'
    4. Emit RabbitMQ message to notification queue
    5. Update job_card status to APPROVAL_PENDING
    6. Return approval record
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    # We would retrieve the customer ID from the job card or estimate in a real implementation
    # Using a dummy UUID for the skeleton
    import uuid
    dummy_customer_id = uuid.uuid4()
    
    approval = CustomerApproval(
        tenant_id=tenant_id,
        job_card_id=job_card_id,
        estimate_id=estimate_id,
        customer_id=dummy_customer_id,
        approval_token=token,
        token_expires_at=expires_at,
        status="pending",
        notification_sent_at=datetime.now(timezone.utc)
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    
    # Trigger message via RabbitMQ would happen here
    # We would also update the job_card state
    
    return approval

async def process_approval_response(db: AsyncSession, token: str, decision: str, ip: str, signature_ref: Optional[str]) -> CustomerApproval:
    """
    1. Fetch approval by token - raise 404 if not found
    2. Raise 410 GONE if token_expires_at < now()
    3. Raise 409 if status != 'pending'
    4. Update status to approved/rejected, record ip_address, approved_at
    5. If approved: transition job_card to APPROVED (calls state machine)
    6. If rejected: transition job_card back to ESTIMATE
    7. Emit notification to customer confirming decision
    8. Invalidate token (set token_expires_at = now())
    9. Write audit_log entry
    """
    result = await db.execute(select(CustomerApproval).where(CustomerApproval.approval_token == token))
    approval = result.scalar_one_or_none()
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval token not found")
        
    now = datetime.now(timezone.utc)
    
    # Check if tz-aware
    expires = approval.token_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
        
    if expires < now:
        raise HTTPException(status_code=410, detail="Approval token has expired")
        
    if approval.status != "pending":
        raise HTTPException(status_code=409, detail=f"Approval already processed with status: {approval.status}")
        
    if decision not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")
        
    approval.status = decision
    approval.ip_address = ip
    approval.e_signature_ref = signature_ref
    
    if decision == "approved":
        approval.approved_at = now
    elif decision == "rejected":
        approval.rejection_reason = "Customer manually rejected the estimate"
        
    approval.token_expires_at = now  # Invalidate token
    
    await db.commit()
    await db.refresh(approval)
    
    # Handle state transition logic and emit RabbitMQ event
    
    return approval
