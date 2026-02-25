import asyncio
from datetime import date, datetime, timezone
from uuid import UUID
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy import Column, String, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.db.base import Base

class DataExportRequest(Base):
    __tablename__ = "data_export_requests"
    id = Column(PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    requested_by = Column(PGUUID(as_uuid=True), nullable=False)
    export_type = Column(String, nullable=False)
    date_range_start = Column(Date, nullable=True)
    date_range_end = Column(Date, nullable=True)
    format = Column(String, nullable=False, default='csv')
    status = Column(String, nullable=False, default='queued')
    s3_url = Column(String, nullable=True)
    s3_url_expires_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

async def request_export(db: AsyncSession, tenant_id: UUID, requested_by: UUID, export_type: str, date_range_start: date, date_range_end: date, format: str) -> DataExportRequest:
    """
    1. Insert data_export_requests record with status='queued'
    2. Emit RabbitMQ message to queue 'data.export.jobs'
    3. Return request record with ETA estimate
    """
    export_req = DataExportRequest(
        tenant_id=tenant_id,
        requested_by=requested_by,
        export_type=export_type,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
        format=format,
        status='queued'
    )
    db.add(export_req)
    await db.commit()
    await db.refresh(export_req)
    # Emission to RabbitMQ goes here
    return export_req

async def process_export_job(db: AsyncSession, request_id: UUID):
    """
    Worker function (called by RabbitMQ consumer):
    1. Fetch all relevant records for tenant
    2. Serialize to requested format (csv/json/pdf)
    3. Upload to S3 with 24-hour pre-signed URL
    4. Update data_export_requests
    5. Send email notification
    """
    result = await db.execute(select(DataExportRequest).filter(DataExportRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        return
        
    try:
        req.status = 'processing'
        await db.commit()
        
        # Stub: Generate the export...
        await asyncio.sleep(1) # simulate work
        
        req.status = 'ready'
        req.s3_url = "https://s3.amazonaws.com/dummy-bucket/export.zip"
        import datetime as dt
        req.s3_url_expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=24)
        req.completed_at = dt.datetime.now(dt.timezone.utc)
        
        await db.commit()
    except Exception as e:
        req.status = 'failed'
        req.error_message = str(e)
        await db.commit()
