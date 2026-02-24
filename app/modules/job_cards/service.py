from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import model, schema
from app.db.models import AuditLog

# Define the allowed state transitions
ALLOWED_TRANSITIONS = {
    "OPEN": ["DIAGNOSIS", "CANCELLED"],
    "DIAGNOSIS": ["ESTIMATE_PENDING", "CANCELLED"],
    "ESTIMATE_PENDING": ["APPROVAL_PENDING", "CANCELLED"],
    "APPROVAL_PENDING": ["APPROVED", "REJECTED", "CANCELLED"],
    "APPROVED": ["REPAIR", "CANCELLED"],
    "REJECTED": ["ESTIMATE_PENDING", "CANCELLED"],
    "REPAIR": ["QC_PDI", "CANCELLED"],
    "QC_PDI": ["READY", "CANCELLED"],
    "READY": ["INVOICED", "CANCELLED"],
    "INVOICED": ["PAID", "CANCELLED"],
    "PAID": ["CLOSED"],
    "CLOSED": [],
    "CANCELLED": [],
}

def _log_audit(db: Session, entity_type: str, entity_id: int, actor_id: str, action: str, payload: dict, tenant_id: str):
    audit_log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        action=action,
        payload=payload,
        tenant_id=tenant_id
    )
    db.add(audit_log)

def create_job_card(db: Session, job_card: schema.JobCardCreate, tenant_id: str, user_id: str):
    # Placeholder for creating a job card without db
    from datetime import datetime
    return model.JobCard(
        id=1,
        job_no="JB-0001",
        tenant_id=tenant_id,
        created_by=user_id,
        state="OPEN",
        complaint=job_card.complaint,
        vehicle_id=job_card.vehicle_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

def get_job_card(db: Session, job_card_id: int, tenant_id: str):
    job_card = db.query(model.JobCard).filter(model.JobCard.id == job_card_id, model.JobCard.tenant_id == tenant_id).first()
    if not job_card:
        raise HTTPException(status_code=404, detail="Job card not found")
    return job_card

def transition_job_card_state(db: Session, job_card_id: int, new_state: str, tenant_id: str, user_id: str):
    db_job_card = get_job_card(db, job_card_id, tenant_id)

    if new_state not in ALLOWED_TRANSITIONS.get(db_job_card.state, []):
        raise HTTPException(status_code=400, detail=f"Invalid state transition from {db_job_card.state} to {new_state}")

    # Add more complex rules here, e.g., check for approved estimate before moving to REPAIR
    if new_state == "REPAIR":
        estimate = db.query(model.Estimate).filter(model.Estimate.job_id == job_card_id, model.Estimate.approved == True).first()
        if not estimate:
            raise HTTPException(status_code=400, detail="Cannot move to REPAIR without an approved estimate.")

    old_state = db_job_card.state
    db_job_card.state = new_state
    
    _log_audit(db, "job_card", db_job_card.id, user_id, "transition_state", {"old_state": old_state, "new_state": new_state}, tenant_id)
    db.commit()
    db.refresh(db_job_card)

    return db_job_card

def create_estimate(db: Session, job_card_id: int, estimate: schema.EstimateCreate, tenant_id: str, user_id: str):
    db_job_card = get_job_card(db, job_card_id, tenant_id)
    
    # In a real app, you would fetch prices from a catalog
    total_parts = sum(line.price * line.quantity for line in estimate.lines)
    total_labor = 500 # Placeholder
    tax_breakdown = {"GST@18": total_parts * 0.18} # Placeholder

    db_estimate = model.Estimate(
        job_id=job_card_id,
        lines=[line.dict() for line in estimate.lines],
        total_parts=total_parts,
        total_labor=total_labor,
        tax_breakdown=tax_breakdown,
        tenant_id=tenant_id
    )
    db.add(db_estimate)
    
    # Transition job card state
    transition_job_card_state(db, job_card_id, "ESTIMATE_PENDING", tenant_id, user_id)
    
    _log_audit(db, "estimate", db_estimate.id, user_id, "create", db_estimate.__dict__, tenant_id)
    db.commit()
    db.refresh(db_estimate)
    
    return db_estimate