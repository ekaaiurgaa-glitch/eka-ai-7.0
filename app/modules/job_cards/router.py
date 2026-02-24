from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schema, service
from app.core.dependencies import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.post("/job-cards", response_model=schema.JobCard)
def create_job_card(
    job_card: schema.JobCardCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new job card (alias endpoint)."""
    user_id = current_user.get("sub")
    tenant_id = "some_tenant_id"
    return service.create_job_card(db=db, job_card=job_card, tenant_id=tenant_id, user_id=user_id)

@router.post("/job_cards", response_model=schema.JobCard)
def create_job_card(
    job_card: schema.JobCardCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    tenant_id = "some_tenant_id" # This should be extracted from the user's token or context
    return service.create_job_card(db=db, job_card=job_card, tenant_id=tenant_id, user_id=user_id)

@router.get("/job-cards/{job_card_id}", response_model=schema.JobCard)
def read_job_card_alias(job_card_id: int, db: Session = Depends(get_db)):
    """Get job card by ID (alias endpoint)."""
    tenant_id = "some_tenant_id"
    return service.get_job_card(db=db, job_card_id=job_card_id, tenant_id=tenant_id)

@router.get("/job_cards/{job_card_id}", response_model=schema.JobCard)
def read_job_card(job_card_id: int, db: Session = Depends(get_db)):
    tenant_id = "some_tenant_id" # This should be extracted from the user's token or context
    return service.get_job_card(db=db, job_card_id=job_card_id, tenant_id=tenant_id)

@router.patch("/job-cards/{job_card_id}/transition", response_model=schema.JobCard)
def transition_job_card_alias(
    job_card_id: int,
    transition: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Transition job card state (alias endpoint)."""
    user_id = current_user.get("sub")
    tenant_id = "some_tenant_id"
    new_state = transition.get("new_state")
    return service.transition_job_card_state(db, job_card_id, new_state, tenant_id, user_id)

@router.patch("/job_cards/{job_card_id}/transition", response_model=schema.JobCard)
def transition_job_card(
    job_card_id: int,
    transition: dict, # e.g., {"new_state": "DIAGNOSIS"}
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    tenant_id = "some_tenant_id"
    new_state = transition.get("new_state")
    return service.transition_job_card_state(db, job_card_id, new_state, tenant_id, user_id)

@router.post("/job-cards/{job_card_id}/estimate", response_model=schema.Estimate)
def create_estimate_alias(
    job_card_id: int,
    estimate: schema.EstimateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create estimate for job card (alias endpoint)."""
    user_id = current_user.get("sub")
    tenant_id = "some_tenant_id"
    return service.create_estimate(db, job_card_id, estimate, tenant_id, user_id)

@router.post("/job_cards/{job_card_id}/estimate", response_model=schema.Estimate)
def create_estimate(
    job_card_id: int,
    estimate: schema.EstimateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    tenant_id = "some_tenant_id"
    return service.create_estimate(db, job_card_id, estimate, tenant_id, user_id)

# The 'approve' endpoint would be similar, transitioning the state to 'APPROVED'
# and likely requiring a specific user role.