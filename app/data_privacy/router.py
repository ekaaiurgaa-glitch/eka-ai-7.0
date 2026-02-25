"""Data Compliance API Router."""
from fastapi import APIRouter, Depends
from app.core.dependencies import get_tenant_id
from app.data_privacy.compliance import export_user_data, delete_user_data, anonymize_data

router = APIRouter(prefix="/data-privacy", tags=["Data Privacy"])

@router.post("/export")
async def export_data(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    return await export_user_data(tenant_id, user_id)

@router.post("/delete")
async def delete_data(
    user_id: str,
    reason: str,
    tenant_id: str = Depends(get_tenant_id)
):
    return await delete_user_data(tenant_id, user_id)

@router.post("/anonymize")
async def anonymize(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    return await anonymize_data(tenant_id, user_id)
