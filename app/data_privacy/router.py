from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel
from app.core.dependencies import get_db, get_tenant_id
from app.core.rbac import require_role
from .export_service import request_export, DataExportRequest
from .deletion_service import request_account_deletion, delete_customer_pii

router = APIRouter(prefix="/v1", tags=["privacy"])

class ExportRequestSchema(BaseModel):
    export_type: str
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    format: str = "csv"

class CustomerDeleteRequest(BaseModel):
    customer_id: UUID

@router.post("/data-export/request")
async def request_export_data(
    req: ExportRequestSchema,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    user: dict = Depends(require_role(["owner"])),
):
    export_req = await request_export(
        db, 
        tenant_id, 
        UUID(user["sub"]), 
        req.export_type, 
        req.date_range_start, 
        req.date_range_end, 
        req.format
    )
    return {"status": "queued", "request_id": str(export_req.id)}

@router.get("/data-export/{request_id}")
async def check_export_status(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    _: dict = Depends(require_role(["owner"])),
):
    from sqlalchemy import select
    result = await db.execute(select(DataExportRequest).filter(DataExportRequest.id == request_id, DataExportRequest.tenant_id == tenant_id))
    export_req = result.scalar_one_or_none()
    
    if not export_req:
        raise HTTPException(status_code=404, detail="Export request not found")
        
    return {"status": export_req.status}

@router.get("/data-export/{request_id}/download")
async def download_export(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    _: dict = Depends(require_role(["owner"])),
):
    from sqlalchemy import select
    import datetime as dt
    result = await db.execute(select(DataExportRequest).filter(DataExportRequest.id == request_id, DataExportRequest.tenant_id == tenant_id))
    export_req = result.scalar_one_or_none()
    
    if not export_req:
        raise HTTPException(status_code=404, detail="Export request not found")
    
    if export_req.status != "ready":
        raise HTTPException(status_code=400, detail=f"Export not ready. Current status: {export_req.status}")
        
    now = dt.datetime.now(dt.timezone.utc)
    if export_req.s3_url_expires_at and export_req.s3_url_expires_at < now:
        raise HTTPException(status_code=410, detail="Download URL has expired. Please request a new export.")
        
    return {"download_url": export_req.s3_url}

@router.post("/privacy/delete-account")
async def schedule_account_deletion(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    user: dict = Depends(require_role(["owner"])),
):
    res = await request_account_deletion(db, tenant_id, UUID(user["sub"]))
    return res

@router.post("/privacy/cancel-deletion")
async def cancel_pending_deletion(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    _: dict = Depends(require_role(["owner"])),
):
    from sqlalchemy import text
    await db.execute(
        text("UPDATE tenants SET deletion_scheduled_at = NULL WHERE id = :tenant_id AND deletion_scheduled_at IS NOT NULL"),
        {"tenant_id": tenant_id}
    )
    await db.commit()
    return {"message": "Account deletion cancelled"}

@router.post("/privacy/delete-customer")
async def right_to_erasure_customer(
    req: CustomerDeleteRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    _: dict = Depends(require_role(["owner"])),
):
    res = await delete_customer_pii(db, req.customer_id, tenant_id)
    return res
