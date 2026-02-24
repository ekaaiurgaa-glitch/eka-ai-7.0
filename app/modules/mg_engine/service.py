from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, model
from .deterministic_engine import calculate_mg


async def get_mg_calculation_and_save_proposal(
    db: AsyncSession, request: schema.MGCalculationRequest
) -> schema.MGCalculationResponse:
    """
    Wraps the deterministic engine and saves the resulting proposal to the database.
    The deterministic calculation is synchronous by design — no AI/async needed.
    """
    calculation_response = calculate_mg(request)

    db_proposal = model.MGProposal(
        tenant_id=request.tenant_id,
        vehicle_id=None,  # Will be linked when Vehicle model is wired via FK
        proposal_json=calculation_response.model_dump(),
        monthly_mg=calculation_response.monthly_mg,
    )
    db.add(db_proposal)
    await db.commit()

    return calculation_response