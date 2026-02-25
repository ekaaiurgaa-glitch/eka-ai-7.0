"""Disaster Recovery API Router."""
from fastapi import APIRouter, Depends
from app.core.dependencies import get_tenant_id
from app.core.disaster_recovery import dr_service

router = APIRouter(prefix="/dr", tags=["Disaster Recovery"])

@router.get("/status")
async def get_dr_status(tenant_id: str = Depends(get_tenant_id)):
    return await dr_service.get_status()

@router.post("/backup")
async def create_backup(tenant_id: str = Depends(get_tenant_id)):
    return await dr_service.backup(tenant_id)

@router.post("/restore")
async def restore_backup(backup_id: str, region: str, tenant_id: str = Depends(get_tenant_id)):
    return await dr_service.restore(backup_id, region)

@router.post("/failover")
async def failover(region: str, tenant_id: str = Depends(get_tenant_id)):
    return await dr_service.failover(region)
