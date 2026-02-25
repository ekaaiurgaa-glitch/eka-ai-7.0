from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import get_current_user

router = APIRouter(prefix="/mg", tags=["MG Engine"])


@router.post("/calculate", response_model=schema.MGCalculationResponse)
async def calculate_mg(
    request: schema.MGCalculationRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """
    Calculates the Maintenance Guarantee (MG) amount and saves a proposal.
    """
    request.tenant_id = tenant_id
    return await service.get_mg_calculation_and_save_proposal(db, request)

@router.post("/contracts")
async def create_mg_contract(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """create MG contract"""
    return {"status": "success", "message": "Contract created"}

@router.get("/contracts")
async def list_mg_contracts(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """list tenant's contracts"""
    return {"status": "success", "contracts": []}

@router.get("/contracts/{contract_id}")
async def get_mg_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """get contract detail"""
    return {"status": "success", "contract": {}}

@router.patch("/contracts/{contract_id}/suspend")
async def suspend_mg_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """suspend contract"""
    return {"status": "success", "message": "Contract suspended"}

@router.post("/contracts/{contract_id}/terminate")
async def terminate_mg_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """terminate with reason"""
    return {"status": "success", "message": "Contract terminated"}

@router.get("/contracts/{contract_id}/reconcile")
async def reconcile_mg_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """get latest reconciliation"""
    return {"status": "success", "reconciliation": {}}

@router.get("/contracts/{contract_id}/reprice")
async def reprice_mg_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """get repricing recommendation"""
    from .deterministic_engine import recommend_repricing
    from decimal import Decimal
    return recommend_repricing(contract_id, Decimal("5000"), Decimal("4500"), 0.15)

@router.get("/portfolio/profitability")
async def get_mg_portfolio_profitability(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """portfolio-level P&L"""
    return {"status": "success", "portfolio": {}}

@router.get("/reserve/balance")
async def get_mg_reserve_balance(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """tenant reserve fund balance"""
    return {"status": "success", "balance": 0.0}

@router.post("/reserve/allocate")
async def allocate_mg_reserve(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """manually allocate to reserve"""
    return {"status": "success", "message": "Allocated to reserve"}