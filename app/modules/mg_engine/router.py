from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schema, service
from app.core.dependencies import get_db

router = APIRouter()

@router.post("/mg/calculate", response_model=schema.MGCalculationResponse)
def calculate_mg(
    request: schema.MGCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Calculates the Maintenance Guarantee (MG) amount and saves a proposal.
    - Validates inputs.
    - Calls the deterministic engine.
    - Saves the proposal for later contract creation.
    """
    return service.get_mg_calculation_and_save_proposal(db, request)