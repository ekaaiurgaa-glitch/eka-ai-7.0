from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict
from app.core.dependencies import get_db, get_tenant_id
from app.core.rbac import require_role
from .pdi_service import create_pdi_record, get_pdi_record, update_pdi_checklist, add_pdi_photos

router = APIRouter(prefix="/v1/jobs", tags=["pdi"])

class PDIChecklistRequest(BaseModel):
    checklist: List[Dict[str, Any]]
    inspector_id: UUID
    model_config = ConfigDict(extra="forbid")

class PDIPhotosRequest(BaseModel):
    photo_urls: List[str]
    model_config = ConfigDict(extra="forbid")

@router.post("/{job_card_id}/pdi")
async def create_pdi(
    job_card_id: UUID,
    request: PDIChecklistRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    _: dict = Depends(require_role(["technician", "manager"]))
):
    try:
        pdi = await create_pdi_record(db, tenant_id, job_card_id, request.inspector_id, request.checklist)
        return {"id": str(pdi.id), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{job_card_id}/pdi")
async def get_pdi(
    job_card_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    _: dict = Depends(require_role(["technician", "manager", "owner"]))
):
    pdi = await get_pdi_record(db, tenant_id, job_card_id)
    return pdi

@router.patch("/{job_card_id}/pdi")
async def update_pdi(
    job_card_id: UUID,
    request: PDIChecklistRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    _: dict = Depends(require_role(["technician", "manager"]))
):
    pdi = await update_pdi_checklist(db, tenant_id, job_card_id, request.checklist)
    return pdi

@router.post("/{job_card_id}/pdi/photos")
async def upload_photos(
    job_card_id: UUID,
    request: PDIPhotosRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    _: dict = Depends(require_role(["technician", "manager"]))
):
    # In a real app this endpoint might accept multipart/form-data with actual files
    # to proxy to S3, but we follow the spec "upload photos to S3, append URLs to PDI record"
    # Assuming S3 upload handled by client or separate orchestrator, and we just append URLs.
    pdi = await add_pdi_photos(db, tenant_id, job_card_id, request.photo_urls)
    return pdi
