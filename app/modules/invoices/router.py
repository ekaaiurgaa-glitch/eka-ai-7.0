from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service, pdf_generator
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import require_permission

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("", response_model=schema.Invoice)
async def create_invoice(
    invoice: schema.InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_create_invoice")),
):
    """Generate an invoice for a completed job card."""
    return await service.create_invoice(db=db, invoice=invoice, tenant_id=tenant_id)


@router.get("", response_model=list[schema.Invoice])
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_create_invoice")),
):
    """List all invoices for tenant."""
    return await service.list_invoices(db, tenant_id)


@router.get("/{invoice_id}", response_model=schema.Invoice)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_create_invoice")),
):
    """Get an invoice by ID."""
    db_invoice = await service.get_invoice(db=db, invoice_id=invoice_id, tenant_id=tenant_id)
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice


@router.get("/job/{job_id}", response_model=schema.Invoice)
async def get_invoice_by_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_create_invoice")),
):
    """Get an invoice for a specific job card."""
    db_invoice = await service.get_invoice_by_job(db=db, job_id=job_id, tenant_id=tenant_id)
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found for this job")
    return db_invoice


@router.post("/{invoice_id}/pay", response_model=schema.Invoice)
async def mark_invoice_paid(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_create_invoice"))
):
    """Mark invoice as paid."""
    db_invoice = await service.mark_paid(db, invoice_id, tenant_id)
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice


@router.get("/{invoice_id}/download")
async def download_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_create_invoice"))
):
    """Download invoice as PDF (P2-1)."""
    from .pdf_generator import generate_invoice_pdf
    from app.modules.job_cards.service import get_job_card
    from app.modules.vehicles.service import get_vehicle
    from app.db.models import Tenant
    
    # 1. Get Invoice
    db_invoice = await service.get_invoice(db, invoice_id, tenant_id)
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # 2. Get Related Data
    job_card = await get_job_card(db, db_invoice.job_id, tenant_id)
    vehicle = await get_vehicle(db, job_card.vehicle_id, tenant_id)
    
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    
    # 3. Prepare objects for PDF
    invoice_data = {
        "id": db_invoice.id,
        "created_at": db_invoice.created_at.strftime("%Y-%m-%d"),
        "lines": db_invoice.lines,
        "total_amount": db_invoice.total_amount,
        "tax_amount": db_invoice.tax_amount
    }
    
    tenant_data = {
        "name": tenant.name if tenant else "EKA Workshop",
        "gst_number": tenant.gst_number if tenant else "N/A",
        "city": tenant.city if tenant else "",
        "state": tenant.state if tenant else ""
    }
    
    customer_data = {
        "name": vehicle.owner_name if vehicle else "Customer",
        "plate_number": vehicle.plate_number if vehicle else "N/A",
        "make": vehicle.make if vehicle else "",
        "model": vehicle.model if vehicle else ""
    }
    
    # 4. Generate
    pdf_buffer = generate_invoice_pdf(invoice_data, tenant_data, customer_data)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"}
    )


@router.get("/export/csv")
async def export_invoices_csv(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_create_invoice"))
):
    """Export invoices as CSV (P2-7)."""
    import csv
    import io
    from .service import list_invoices
    
    invoices = await list_invoices(db, tenant_id)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Invoice ID", "Job ID", "Date", "Total Amount", "Tax Amount", "Status"])
    
    for inv in invoices:
        writer.writerow([
            inv.id,
            inv.job_id,
            inv.created_at.strftime("%Y-%m-%d"),
            inv.total_amount,
            inv.tax_amount,
            inv.status
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=invoices_export.csv"}
    )
