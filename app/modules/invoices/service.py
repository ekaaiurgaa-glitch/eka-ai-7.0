import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from . import model, schema


async def create_invoice(db: AsyncSession, invoice: schema.InvoiceCreate, tenant_id: str) -> model.Invoice:
    from app.db.models import Tenant
    result = await db.execute(sa.select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    
    tenant_state = tenant.state if tenant else "Generic State"
    # In a real app, supply_state would come from customer record
    supply_state = tenant_state 

    total_taxable = 0
    total_cgst = 0
    total_sgst = 0
    total_igst = 0

    processed_lines = []
    for line in invoice.lines:
        taxable_value = line.price * line.quantity
        rate = line.tax_rate  # In percent, e.g. 18.0
        
        line_tax_info = {
            "taxable_value": taxable_value,
            "cgst": 0,
            "sgst": 0,
            "igst": 0,
            "total": 0
        }
        
        if supply_state == tenant_state:
            line_tax_info["cgst"] = taxable_value * (rate / 200)
            line_tax_info["sgst"] = taxable_value * (rate / 200)
        else:
            line_tax_info["igst"] = taxable_value * (rate / 100)
            
        line_tax_info["total"] = taxable_value + line_tax_info["cgst"] + line_tax_info["sgst"] + line_tax_info["igst"]
        
        total_taxable += taxable_value
        total_cgst += line_tax_info["cgst"]
        total_sgst += line_tax_info["sgst"]
        total_igst += line_tax_info["igst"]
        
        processed_lines.append({
            **line.model_dump(),
            "gst_details": line_tax_info
        })

    final_tax = total_cgst + total_sgst + total_igst
    final_total = total_taxable + final_tax

    db_invoice = model.Invoice(
        job_id=invoice.job_id,
        lines=processed_lines,
        total_amount=round(float(final_total), 2),
        tax_amount=round(float(final_tax), 2),
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
