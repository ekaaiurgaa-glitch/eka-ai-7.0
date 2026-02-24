from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import analytics_service
from app.core.dependencies import get_db

router = APIRouter()

@router.get("/dashboard/{dashboard_type}")
def get_dashboard(
    dashboard_type: str,
    db: Session = Depends(get_db)
):
    """
    Returns data for a specific dashboard type.
    - `workshop`: Revenue, job states, pending approvals.
    - `fleet`: MG commitments, cost per vehicle.
    - `owner`: Service history, upcoming service.
    """
    tenant_id = "some_tenant_id" # This should be extracted from context

    if dashboard_type == "workshop":
        return analytics_service.get_workshop_dashboard_data(db, tenant_id)
    elif dashboard_type == "fleet":
        return analytics_service.get_fleet_dashboard_data(db, tenant_id)
    elif dashboard_type == "owner":
        # Owner dashboard would likely require a vehicle_id
        # vehicle_id = 1 # from user context
        # return analytics_service.get_owner_dashboard_data(db, tenant_id, vehicle_id)
        raise HTTPException(status_code=400, detail="Owner dashboard requires a vehicle_id.")
    else:
        raise HTTPException(status_code=404, detail="Dashboard type not found.")