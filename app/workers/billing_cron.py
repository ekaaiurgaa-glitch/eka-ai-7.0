import asyncio
from datetime import date, datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.subscriptions.models import TenantSubscription
from app.data_privacy.router import DataExportRequest
from app.approvals.models import CustomerApproval

async def process_billing_cycle_renewals():
    """
    Find all tenant_subscriptions where billing_cycle_end = today.
    For each:
    1. If auto_renew and payment_method_ref: attempt renewal via payment gateway
       - Success: extend billing_cycle_end by 30 days, reset usage_aggregates
       - Failure: set status='expired', send email
    2. If not auto_renew: set status='expired', send email
    3. Process any pending overage_ledger entries -> generate overage invoice
    """
    async with AsyncSessionLocal() as db:
        today = date.today()
        result = await db.execute(select(TenantSubscription).where(
            TenantSubscription.billing_cycle_end <= today,
            TenantSubscription.status == 'active'
        ))
        subs = result.scalars().all()
        
        for sub in subs:
            if sub.auto_renew and sub.payment_method_ref:
                # Mock payment gateway success
                payment_success = True
                if payment_success:
                    sub.billing_cycle_start = today
                    sub.billing_cycle_end = today + timedelta(days=30)
                    # Reset usage aggregates here (mock)
                else:
                    sub.status = 'expired'
            else:
                sub.status = 'expired'
                
            # Process overages...
            
        await db.commit()

async def process_mg_monthly_reconciliation():
    """
    Run on 1st of each month.
    For each active tenant with mg_contracts:
      await run_monthly_reconciliation(tenant_id, last_month)
    """
    pass

async def expire_approval_tokens():
    """
    Run every 15 minutes.
    UPDATE customer_approvals SET status='expired' 
    WHERE status='pending' AND token_expires_at < now()
    """
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        result = await db.execute(select(CustomerApproval).where(
            CustomerApproval.status == 'pending',
            CustomerApproval.token_expires_at < now
        ))
        approvals = result.scalars().all()
        
        for approval in approvals:
            approval.status = 'expired'
            
        await db.commit()

async def expire_data_export_urls():
    """
    Run every hour.
    UPDATE data_export_requests SET status='expired'
    WHERE status='ready' AND s3_url_expires_at < now()
    """
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        result = await db.execute(select(DataExportRequest).where(
            DataExportRequest.status == 'ready',
            DataExportRequest.s3_url_expires_at < now
        ))
        requests = result.scalars().all()
        
        for req in requests:
            req.status = 'expired'
            
        await db.commit()
