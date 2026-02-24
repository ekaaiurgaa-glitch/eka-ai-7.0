from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from . import analytics_service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import get_current_user

router = APIRouter()


@router.get("/dashboard/{dashboard_type}")
async def get_dashboard(
    dashboard_type: str,
    vehicle_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
):
    """
    Returns data for a specific dashboard type.
    - `workshop`: Revenue, job states, pending approvals.
    - `fleet`: MG commitments, cost per vehicle.
    - `owner`: Service history, upcoming service (requires `vehicle_id` query param).
    """
    if dashboard_type == "workshop":
        return await analytics_service.get_workshop_dashboard_data(db, tenant_id)
    elif dashboard_type == "fleet":
        return await analytics_service.get_fleet_dashboard_data(db, tenant_id)
    elif dashboard_type == "owner":
        if not vehicle_id:
            raise HTTPException(status_code=400, detail="Owner dashboard requires `vehicle_id` query param.")
        return await analytics_service.get_owner_dashboard_data(db, tenant_id, vehicle_id)
    else:
        raise HTTPException(status_code=404, detail=f"Dashboard type '{dashboard_type}' not found.")