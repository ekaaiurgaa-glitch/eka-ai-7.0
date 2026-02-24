from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import get_current_user, require_permission

router = APIRouter()


@router.post("/job-cards", response_model=schema.JobCard)
async def create_job_card_alias(
    job_card: schema.JobCardCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_jobs")),
):
    return await service.create_job_card(db=db, job_card=job_card, tenant_id=tenant_id, user_id=current_user["sub"])


@router.post("/job_cards", response_model=schema.JobCard)
async def create_job_card(
    job_card: schema.JobCardCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_jobs")),
):
    return await service.create_job_card(db=db, job_card=job_card, tenant_id=tenant_id, user_id=current_user["sub"])


@router.get("/job-cards/{job_card_id}", response_model=schema.JobCard)
async def read_job_card_alias(
    job_card_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    return await service.get_job_card(db=db, job_card_id=job_card_id, tenant_id=tenant_id)


@router.get("/job_cards/{job_card_id}", response_model=schema.JobCard)
async def read_job_card(
    job_card_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    return await service.get_job_card(db=db, job_card_id=job_card_id, tenant_id=tenant_id)


@router.patch("/job-cards/{job_card_id}/transition", response_model=schema.JobCard)
async def transition_job_card_alias(
    job_card_id: int,
    transition: dict,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_jobs")),
):
    return await service.transition_job_card_state(db, job_card_id, transition.get("new_state"), tenant_id, current_user["sub"])


@router.patch("/job_cards/{job_card_id}/transition", response_model=schema.JobCard)
async def transition_job_card(
    job_card_id: int,
    transition: dict,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_jobs")),
):
    return await service.transition_job_card_state(db, job_card_id, transition.get("new_state"), tenant_id, current_user["sub"])


@router.post("/job-cards/{job_card_id}/estimate", response_model=schema.Estimate)
async def create_estimate_alias(
    job_card_id: int,
    estimate: schema.EstimateCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_estimates")),
):
    return await service.create_estimate(db, job_card_id, estimate, tenant_id, current_user["sub"])


@router.post("/job_cards/{job_card_id}/estimate", response_model=schema.Estimate)
async def create_estimate(
    job_card_id: int,
    estimate: schema.EstimateCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_estimates")),
):
    return await service.create_estimate(db, job_card_id, estimate, tenant_id, current_user["sub"])