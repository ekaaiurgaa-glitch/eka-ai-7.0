from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException
from .pdi_models import PDIRecord

async def create_pdi_record(db: AsyncSession, tenant_id: UUID, job_card_id: UUID, inspector_id: UUID, checklist: List[Dict[str, Any]]) -> PDIRecord:
    overall_passed = all(item.get("passed", False) for item in checklist)
    
    pdi = PDIRecord(
        tenant_id=tenant_id,
        job_card_id=job_card_id,
        checklist=checklist,
        overall_passed=overall_passed,
        inspector_id=inspector_id,
        inspected_at=datetime.now(timezone.utc),
        photos=[]
    )
    
    db.add(pdi)
    await db.commit()
    await db.refresh(pdi)
    return pdi

async def get_pdi_record(db: AsyncSession, tenant_id: UUID, job_card_id: UUID) -> PDIRecord:
    result = await db.execute(
        select(PDIRecord).where(
            PDIRecord.job_card_id == job_card_id,
            PDIRecord.tenant_id == tenant_id
        )
    )
    pdi = result.scalar_one_or_none()
    if not pdi:
        raise HTTPException(status_code=404, detail="PDI Record not found")
    return pdi

async def update_pdi_checklist(db: AsyncSession, tenant_id: UUID, job_card_id: UUID, checklist: List[Dict[str, Any]]) -> PDIRecord:
    pdi = await get_pdi_record(db, tenant_id, job_card_id)
    
    overall_passed = all(item.get("passed", False) for item in checklist)
    pdi.checklist = checklist
    pdi.overall_passed = overall_passed
    pdi.inspected_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(pdi)
    return pdi

async def add_pdi_photos(db: AsyncSession, tenant_id: UUID, job_card_id: UUID, photo_urls: List[str]) -> PDIRecord:
    pdi = await get_pdi_record(db, tenant_id, job_card_id)
    
    current_photos = pdi.photos or []
    current_photos.extend(photo_urls)
    pdi.photos = current_photos
    
    await db.commit()
    await db.refresh(pdi)
    return pdi
