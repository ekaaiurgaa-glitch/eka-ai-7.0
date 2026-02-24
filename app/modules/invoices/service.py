from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from . import model, schema


async def create_invoice(db: AsyncSession, invoice: schema.InvoiceCreate, tenant_id: str) -> model.Invoice:
    lines_data = [line.model_dump() for line in invoice.lines]
    total_amount = sum(line.price * line.quantity for line in invoice.lines)
    tax_amount = sum(line.price * line.quantity * line.tax_rate for line in invoice.lines)

    db_invoice = model.Invoice(
        job_id=invoice.job_id,
        lines=lines_data,
        total_amount=round(total_amount, 2),
        tax_amount=round(tax_amount, 2),
        tenant_id=tenant_id,
    )
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice


async def get_invoice(db: AsyncSession, invoice_id: int, tenant_id: str) -> model.Invoice:
    result = await db.execute(
        select(model.Invoice).filter(
            model.Invoice.id == invoice_id, model.Invoice.tenant_id == tenant_id
        )
    )
    return result.scalar_one_or_none()
