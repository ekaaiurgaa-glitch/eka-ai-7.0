from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from . import schema, service, model
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import get_current_user, require_permission

router = APIRouter(prefix="/job-cards", tags=["Job Cards"])


@router.post("", response_model=schema.JobCardResponse)
async def create_job_card(
    job_card: schema.JobCardCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_jobs")),
):
    """Create a new job card."""
    return await service.create_job_card(db=db, job_card=job_card, tenant_id=tenant_id, user_id=current_user["sub"])


@router.get("", response_model=List[schema.JobCardResponse])
async def list_job_cards(
    state: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """List job cards with filters (BRD P1-22)."""
    query = select(model.JobCard).where(model.JobCard.tenant_id == tenant_id)
    if state:
        query = query.where(model.JobCard.state == state)
    
    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()


@router.get("/{job_card_id}", response_model=schema.JobCardResponse)
async def read_job_card(
    job_card_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """Get a job card by ID."""
    return await service.get_job_card(db=db, job_card_id=job_card_id, tenant_id=tenant_id)


@router.patch("/{job_card_id}/transition", response_model=schema.JobCardResponse)
async def transition_job_card(
    job_card_id: int,
    transition: schema.StateTransition,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_jobs")),
):
    """Transition a job card to a new state (FSM)."""
    return await service.transition_job_card_state(db, job_card_id, transition.new_state, tenant_id, current_user["sub"])


@router.post("/{job_card_id}/estimate", response_model=schema.EstimateResponse)
async def create_estimate(
    job_card_id: int,
    estimate: schema.EstimateCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_estimates")),
):
    """Create an estimate for a job card."""
    return await service.create_estimate(db, job_card_id, estimate, tenant_id, current_user["sub"])


@router.post("/{job_card_id}/summarize", response_model=schema.SummarizeResponse)
async def summarize_job_card(
    job_card_id: int,
    force_refresh: bool = False,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """
    Generate AI summary of job card for customer communication.
    """
    return await service.summarize_job_card(
        db=db,
        job_card_id=job_card_id,
        tenant_id=tenant_id,
        force_refresh=force_refresh,
    )
