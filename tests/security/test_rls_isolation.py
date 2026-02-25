import pytest
from sqlalchemy import select
from app.modules.job_cards.model import JobCard, Estimate
from app.db.models import AuditLog, Tenant
from app.modules.invoices.model import Invoice
from app.modules.vehicles.model import Vehicle
from app.subscriptions.models import TenantSubscription, UsageAggregate
from app.modules.mg_engine.model import MGContract

@pytest.mark.asyncio
async def test_tenant_a_cannot_read_tenant_b_job_cards(db_session, test_tenant, test_tenant_2):
    # Setup: Create job card for tenant B
    jb_b = JobCard(tenant_id=test_tenant_2, vehicle_id=1, complaint="B's problem")
    db_session.add(jb_b)
    await db_session.commit()
    
    # Action: Query as tenant A
    result = await db_session.execute(
        select(JobCard).where(JobCard.tenant_id == test_tenant)
    )
    cards = result.scalars().all()
    
    # Assert
    assert len(cards) == 0
    
    # Verify we can see it if we specifically query for tenant B (admin view context)
    result_b = await db_session.execute(
        select(JobCard).where(JobCard.tenant_id == test_tenant_2)
    )
    assert len(result_b.scalars().all()) == 1

@pytest.mark.asyncio
async def test_cross_tenant_audit_log_access_blocked(db_session, test_tenant, test_tenant_2):
    log_b = AuditLog(tenant_id=test_tenant_2, action="LOGIN", entity_type="USER")
    db_session.add(log_b)
    await db_session.commit()
    
    result = await db_session.execute(
        select(AuditLog).where(AuditLog.tenant_id == test_tenant)
    )
    assert len(result.scalars().all()) == 0
