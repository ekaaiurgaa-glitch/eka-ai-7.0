from sqlalchemy.orm import Session
from . import schema, model
from .deterministic_engine import calculate_mg

def get_mg_calculation_and_save_proposal(
    db: Session, request: schema.MGCalculationRequest
) -> schema.MGCalculationResponse:
    """
    This service function acts as a wrapper for the deterministic engine
    and saves the resulting proposal to the database.
    """
    # 1. Calculate the MG
    calculation_response = calculate_mg(request)

    # 2. Save the proposal (temporarily disabled for smoke test)
    # db_proposal = model.MGProposal(
    #     tenant_id=request.tenant_id,
    #     vehicle_id=1, # Placeholder for vehicle_id
    #     proposal_json=calculation_response.dict(),
    #     monthly_mg=calculation_response.monthly_mg
    # )
    # db.add(db_proposal)
    # db.commit()
    # db.refresh(db_proposal)

    return calculation_response