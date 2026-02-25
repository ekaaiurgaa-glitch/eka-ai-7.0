from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, model
from .deterministic_engine import calculate_mg_service


async def get_mg_calculation_and_save_proposal(
    db: AsyncSession, request: schema.MGCalculationRequest
) -> schema.MGCalculationResponse:
    """
    Wraps the deterministic engine and saves the resulting proposal.
    """
    calculation_response = await calculate_mg_service(db, request)

    db_proposal = model.MGProposal(
        tenant_id=request.tenant_id,
        vehicle_id=None,
        proposal_json=calculation_response.model_dump(),
        monthly_mg=calculation_response.monthly_mg,
    )
    db.add(db_proposal)
    await db.commit()

    return calculation_response