from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from . import model, schema
from app.db.models import AuditLog


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


async def _log_audit(db: AsyncSession, entity_type: str, entity_id: str, actor_id: str, action: str, payload: dict, tenant_id: str):
    audit_log = AuditLog(
        entity_type=entity_type,
        entity_id=str(entity_id),
        actor_id=actor_id,
        action=action,
        payload=payload,
        tenant_id=tenant_id,
    )
    db.add(audit_log)


async def _generate_job_no(db: AsyncSession, db_job_card: model.JobCard) -> str:
    # Generate job number from actual ID after commit to guarantee uniqueness
    return f"JB-{db_job_card.id:04d}"


async def create_job_card(db: AsyncSession, job_card: schema.JobCardCreate, tenant_id: str, user_id: str) -> model.JobCard:
    db_job_card = model.JobCard(
        job_no="TEMP",  # Temporary, will update before commit
        tenant_id=tenant_id,
        created_by=user_id,
        state="OPEN",
        complaint=job_card.complaint,
        vehicle_id=job_card.vehicle_id,
    )
    db.add(db_job_card)
    await db.flush()  # Flush to get auto-increment ID without committing
    await db.refresh(db_job_card)
    # Generate job number from actual ID to guarantee uniqueness
    db_job_card.job_no = f"JB-{db_job_card.id:04d}"
    await _log_audit(db, "job_card", db_job_card.id, user_id, "create", {"job_no": db_job_card.job_no}, tenant_id)
    await db.commit()  # Single atomic commit
    return db_job_card


async def get_job_card(db: AsyncSession, job_card_id: int, tenant_id: str) -> model.JobCard:
    result = await db.execute(
        select(model.JobCard).filter(model.JobCard.id == job_card_id, model.JobCard.tenant_id == tenant_id)
    )
    job_card = result.scalar_one_or_none()
    if not job_card:
        raise HTTPException(status_code=404, detail="Job card not found")
    return job_card


async def transition_job_card_state(db: AsyncSession, job_card_id: int, new_state: str, tenant_id: str, user_id: str) -> model.JobCard:
    db_job_card = await get_job_card(db, job_card_id, tenant_id)

    if new_state not in ALLOWED_TRANSITIONS.get(db_job_card.state, []):
        raise HTTPException(status_code=400, detail=f"Invalid state transition from {db_job_card.state} to {new_state}")

    if new_state == "REPAIR":
        result = await db.execute(
            select(model.Estimate).filter(
                model.Estimate.job_id == job_card_id,
                model.Estimate.approved == True,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Cannot move to REPAIR without an approved estimate.")

    old_state = db_job_card.state
    db_job_card.state = new_state
    await _log_audit(db, "job_card", db_job_card.id, user_id, "transition_state", {"old_state": old_state, "new_state": new_state}, tenant_id)
    await db.commit()
    await db.refresh(db_job_card)
    return db_job_card


async def create_estimate(db: AsyncSession, job_card_id: int, estimate: schema.EstimateCreate, tenant_id: str, user_id: str) -> model.Estimate:
    await get_job_card(db, job_card_id, tenant_id)

    # Try to fetch real prices from catalog; fall back to schema prices
    total_parts = 0.0
    total_labor = 500.0
    try:
        from app.modules.catalog.service import get_part, get_labor_rate
        total_parts = sum(line.price * line.quantity for line in estimate.lines)
        labor = await get_labor_rate(db, "general_service", "default", tenant_id)
        if labor:
            # Handle both dict (from cache) and ORM object cases
            if isinstance(labor, dict):
                total_labor = labor["rate_per_hour"] * labor["estimated_hours"]
            else:
                total_labor = labor.rate_per_hour * labor.estimated_hours
    except Exception:
        total_parts = sum(line.price * line.quantity for line in estimate.lines)

    tax_breakdown = {"GST@18": round(total_parts * 0.18, 2)}

    db_estimate = model.Estimate(
        job_id=job_card_id,
        lines=[line.model_dump() for line in estimate.lines],
        total_parts=total_parts,
        total_labor=total_labor,
        tax_breakdown=tax_breakdown,
        tenant_id=tenant_id,
    )
    db.add(db_estimate)
    await db.commit()
    await db.refresh(db_estimate)

    await transition_job_card_state(db, job_card_id, "ESTIMATE_PENDING", tenant_id, user_id)
    await _log_audit(db, "estimate", db_estimate.id, user_id, "create",
                     {"total_parts": total_parts, "total_labor": total_labor}, tenant_id)
    await db.commit()
    return db_estimate