from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import get_current_user

router = APIRouter()


@router.post("/mg/calculate", response_model=schema.MGCalculationResponse)
async def calculate_mg(
    request: schema.MGCalculationRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """
    Calculates the Maintenance Guarantee (MG) amount and saves a proposal.
    Uses the deterministic engine — no AI math is performed here.
    """
    request.tenant_id = tenant_id
    return await service.get_mg_calculation_and_save_proposal(db, request)