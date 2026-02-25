from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import get_current_user, require_permission

router = APIRouter()


@router.post("/job-cards", response_model=schema.JobCardResponse)
async def create_job_card(
    job_card: schema.JobCardCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_jobs")),
):
    """Create a new job card."""
    return await service.create_job_card(db=db, job_card=job_card, tenant_id=tenant_id, user_id=current_user["sub"])


@router.get("/job-cards/{job_card_id}", response_model=schema.JobCardResponse)
async def read_job_card(
    job_card_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """Get a job card by ID."""
    return await service.get_job_card(db=db, job_card_id=job_card_id, tenant_id=tenant_id)


@router.patch("/job-cards/{job_card_id}/transition", response_model=schema.JobCardResponse)
async def transition_job_card(
    job_card_id: int,
    transition: schema.StateTransition,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_jobs")),
):
    """Transition a job card to a new state (FSM)."""
    return await service.transition_job_card_state(db, job_card_id, transition.new_state, tenant_id, current_user["sub"])


@router.post("/job-cards/{job_card_id}/estimate", response_model=schema.EstimateResponse)
async def create_estimate(
    job_card_id: int,
    estimate: schema.EstimateCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_estimates")),
):
    """Create an estimate for a job card."""
    return await service.create_estimate(db, job_card_id, estimate, tenant_id, current_user["sub"])


@router.post("/job-cards/{job_card_id}/summarize", response_model=schema.SummarizeResponse)
async def summarize_job_card(
    job_card_id: int,
    force_refresh: bool = False,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """
    Generate AI summary of job card for customer communication.
    
    - Returns cached summary if available and job state hasn't changed
    - Use force_refresh=true to bypass cache and regenerate
    - Urgency is computed with safety floor (keywords override AI downward)
    """
    return await service.summarize_job_card(
        db=db,
        job_card_id=job_card_id,
        tenant_id=tenant_id,
        force_refresh=force_refresh,
    )
