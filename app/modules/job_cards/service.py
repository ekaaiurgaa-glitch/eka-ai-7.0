from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy as sa
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

    if new_state == "READY" and old_state == "QC_PDI":
        from app.modules.job_cards.pdi_models import PDIRecord
        result = await db.execute(
            select(PDIRecord).filter(
                # Cast the job_card_id to string to match UUID since JobCard is integer currently
                sa.cast(PDIRecord.job_card_id, sa.String) == str(job_card_id),
                PDIRecord.overall_passed == True
            )
        )
        pdi = result.scalar_one_or_none()
        if not pdi:
            raise HTTPException(status_code=409, detail="PDI not completed. Complete and pass PDI inspection before marking READY.")
        if not pdi.photos or len(pdi.photos) == 0:
            raise HTTPException(status_code=409, detail="PDI requires at least one photo. Upload photos before completing PDI.")

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


async def summarize_job_card(
    db: AsyncSession,
    job_card_id: int,
    tenant_id: str,
    force_refresh: bool = False,
) -> schema.SummarizeResponse:
    """
    Generate or retrieve cached AI summary of job card.
    
    Args:
        db: Database session
        job_card_id: ID of job card to summarize
        tenant_id: Tenant isolation
        force_refresh: Bypass cache and regenerate
        
    Returns:
        SummarizeResponse with AI-generated summary
    """
    from app.ai.summarization import summarize_job_card as ai_summarize
    from app.modules.vehicles.service import get_vehicle
    
    # Get job card
    job_card = await get_job_card(db, job_card_id, tenant_id)
    
    # Check for cached summary (unless force_refresh)
    if not force_refresh:
        result = await db.execute(
            select(model.JobSummary).filter(
                model.JobSummary.job_id == job_card_id,
                model.JobSummary.tenant_id == tenant_id,
            )
        )
        cached = result.scalar_one_or_none()
        
        # Cache valid if exists and job state hasn't changed
        if cached and cached.job_state_at_summary == job_card.state:
            return schema.SummarizeResponse(
                job_id=job_card_id,
                job_no=job_card.job_no,
                technical_summary=cached.technical_summary,
                customer_summary=cached.customer_summary,
                urgency=cached.urgency,
                estimated_cost=cached.estimated_cost,
                recommended_action=cached.recommended_action,
                cached=True,
                generated_at=cached.generated_at,
            )
    
    # Get vehicle info
    try:
        vehicle = await get_vehicle(db, job_card.vehicle_id, tenant_id)
        vehicle_info = {
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
        }
    except Exception:
        vehicle_info = {"make": "Unknown", "model": "Unknown", "year": "N/A"}
    
    # Get estimate info
    result = await db.execute(
        select(model.Estimate).filter(
            model.Estimate.job_id == job_card_id,
            model.Estimate.tenant_id == tenant_id,
        )
    )
    estimate = result.scalar_one_or_none()
    
    estimate_parts = estimate.lines if estimate else []
    estimate_total = estimate.total_parts + estimate.total_labor if estimate else 0.0
    
    # Call AI summarization
    ai_result = await ai_summarize(
        job_no=job_card.job_no,
        mechanic_notes=job_card.complaint,
        vehicle_info=vehicle_info,
        estimate_parts=estimate_parts,
        estimate_total=estimate_total,
    )
    
    # Cache the result
    summary_data = {
        "job_id": job_card_id,
        "tenant_id": tenant_id,
        "job_state_at_summary": job_card.state,
        "technical_summary": ai_result["technical_summary"],
        "customer_summary": ai_result["customer_summary"],
        "urgency": ai_result["urgency"],
        "estimated_cost": ai_result["estimated_cost"],
        "recommended_action": ai_result["recommended_action"],
        "generated_at": datetime.now(timezone.utc),
    }
    
    # Upsert: delete old if exists, insert new
    result = await db.execute(
        select(model.JobSummary).filter(
            model.JobSummary.job_id == job_card_id,
            model.JobSummary.tenant_id == tenant_id,
        )
    )
    old_summary = result.scalar_one_or_none()
    if old_summary:
        await db.delete(old_summary)
        await db.flush()  # Flush delete before insert
    
    new_summary = model.JobSummary(**summary_data)
    db.add(new_summary)
    await db.commit()
    
    return schema.SummarizeResponse(
        job_id=job_card_id,
        job_no=job_card.job_no,
        technical_summary=ai_result["technical_summary"],
        customer_summary=ai_result["customer_summary"],
        urgency=ai_result["urgency"],
        estimated_cost=ai_result["estimated_cost"],
        recommended_action=ai_result["recommended_action"],
        cached=False,
        generated_at=summary_data["generated_at"],
    )
