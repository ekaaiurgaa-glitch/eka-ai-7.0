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


async def list_invoices(db: AsyncSession, tenant_id: str) -> list[model.Invoice]:
    result = await db.execute(
        sa.select(model.Invoice).where(model.Invoice.tenant_id == tenant_id)
    )
    return result.scalars().all()


async def mark_paid(db: AsyncSession, invoice_id: int, tenant_id: str) -> model.Invoice:
    db_invoice = await get_invoice(db, invoice_id, tenant_id)
    if not db_invoice:
        return None
    db_invoice.status = "PAID"
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice


async def generate_invoice_from_job_card(db: AsyncSession, job_card_id: int, tenant_id: str) -> model.Invoice:
    """
    Automatically generates an invoice from the approved estimate of a job card.
    """
    from app.modules.job_cards.model import JobCard, Estimate
    
    # 1. Get JobCard
    result = await db.execute(
        select(JobCard).filter(JobCard.id == job_card_id, JobCard.tenant_id == tenant_id)
    )
    job_card = result.scalar_one_or_none()
    if not job_card:
        raise HTTPException(status_code=404, detail="Job card not found")

    # 2. Get Approved Estimate
    result = await db.execute(
        select(Estimate).filter(
            Estimate.job_id == job_card_id, 
            Estimate.approved == True,
            Estimate.tenant_id == tenant_id
        )
    )
    estimate = result.scalar_one_or_none()
    if not estimate:
        # Fallback: get latest estimate if none approved (logic might vary)
        result = await db.execute(
            select(Estimate).filter(
                Estimate.job_id == job_card_id, 
                Estimate.tenant_id == tenant_id
            ).order_by(Estimate.created_at.desc())
        )
        estimate = result.scalar_one_or_none()
        
    if not estimate:
        raise HTTPException(status_code=400, detail="No estimate found for this job card. Cannot generate invoice.")

    # 3. Construct Invoice Lines
    invoice_lines = []
    
    # Add part lines from estimate
    for line in estimate.lines:
        invoice_lines.append(schema.InvoiceLine(
            part_id=line.get("part_id"),
            description=line.get("description", "Part"),
            quantity=line.get("quantity", 1),
            price=line.get("price", 0.0),
            tax_rate=line.get("tax_rate", 18.0) if line.get("tax_rate", 18.0) > 1 else line.get("tax_rate", 0.18) * 100,
            hsn_code=line.get("hsn_code")
        ))
    
    # Add Labor line if present
    if estimate.total_labor > 0:
        invoice_lines.append(schema.InvoiceLine(
            description="Labor Charges",
            quantity=1,
            price=estimate.total_labor,
            tax_rate=18.0  # Standard labor GST
        ))

    # 4. Create the Invoice
    invoice_create = schema.InvoiceCreate(
        job_id=job_card_id,
        lines=invoice_lines
    )
    return await create_invoice(db, invoice_create, tenant_id)


async def get_invoice_by_job(db: AsyncSession, job_id: int, tenant_id: str) -> model.Invoice:
    """Fetch invoice associated with a specific job card."""
    result = await db.execute(
        select(model.Invoice).filter(
            model.Invoice.job_id == job_id, model.Invoice.tenant_id == tenant_id
        )
    )
    return result.scalar_one_or_none()
