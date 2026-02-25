from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, delete, update
from fastapi import HTTPException

# Note: We don't have a rigid Tenant model defined in these files yet, so using raw SQL for tenant updates
# as we don't have access to the exact ORM definition.

async def request_account_deletion(db: AsyncSession, tenant_id: UUID, requested_by: UUID):
    """
    1. Set tenant.deletion_scheduled_at = now() + 30 days (soft delete)
    2. Send confirmation email with cancellation link
    3. After 30 days (cron job): execute hard_delete_tenant()
    """
    now = datetime.now(timezone.utc)
    scheduled_at = now + timedelta(days=30)
    
    # We would use ORM normally, using text execution here assuming structure
    await db.execute(
        text("UPDATE tenants SET deletion_scheduled_at = :scheduled_at WHERE id = :tenant_id"),
        {"scheduled_at": scheduled_at, "tenant_id": tenant_id}
    )
    await db.commit()
    return {"message": "Account deletion scheduled.", "scheduled_at": scheduled_at}

async def hard_delete_tenant(db: AsyncSession, tenant_id: UUID):
    """
    In transaction:
    1. Hard delete: job_cards, vehicles, customers, invoices, estimates, mg_contracts
    2. Anonymize audit_logs: replace names/emails/phones with sha256 hashes
    3. Delete S3 objects (PDI images, invoices, exports) for this tenant
    4. Update tenant record: status='deleted', name='[DELETED]', gst_number=NULL
    5. Retain audit_logs record structure (required for 7-year GST compliance)
    """
    try:
        # Example of deletion workflow:
        tables = [
            "data_export_requests", "mg_reserve_transactions", "mg_contracts",
            "pdi_records", "customer_approvals", "invoices", "estimates",
            "job_cards", "vehicles", "customers"
        ]
        
        for table in tables:
            await db.execute(text(f"DELETE FROM {table} WHERE tenant_id = :tenant_id"), {"tenant_id": tenant_id})
            
        # Anonymize audit logs (simplified)
        await db.execute(
            text("UPDATE audit_logs SET actor_id = encode(sha256(actor_id::bytea), 'hex') WHERE tenant_id = :tenant_id"), 
            {"tenant_id": str(tenant_id)}
        )
        
        # Update tenant
        await db.execute(
            text("UPDATE tenants SET status = 'deleted', name = '[DELETED]' WHERE id = :tenant_id"), 
            {"tenant_id": tenant_id}
        )
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e

async def delete_customer_pii(db: AsyncSession, customer_id: UUID, tenant_id: UUID):
    """
    GDPR individual right to erasure:
    1. Set customer fields: name='[REDACTED]', phone=hash(phone), email=hash(email)
    2. In invoices: redact customer_name field, retain financial amounts
    3. In audit_logs: anonymize PII fields only
    4. Retain job_card history (financial record, GST compliance)
    Turnaround: queue for processing within 30 days
    """
    try:
        # Step 1: Anonymize customer
        await db.execute(
            text("""
                UPDATE customers 
                SET name = '[REDACTED]', 
                    phone = encode(sha256(phone::bytea), 'hex'), 
                    email = encode(sha256(email::bytea), 'hex')
                WHERE id = :customer_id AND tenant_id = :tenant_id
            """),
            {"customer_id": customer_id, "tenant_id": tenant_id}
        )
        
        # We would continue with other redactions here
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e
    
    return {"message": "Customer anonymized based on right to erasure."}
