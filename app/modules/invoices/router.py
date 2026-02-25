from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
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
