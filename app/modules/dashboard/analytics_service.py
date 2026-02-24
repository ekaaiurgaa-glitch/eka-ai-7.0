from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.modules.job_cards.model import JobCard, Estimate
from app.modules.invoices.model import Invoice


async def get_workshop_dashboard_data(db: AsyncSession, tenant_id: str) -> dict:
    """Real dashboard queries from the DB."""
    # Jobs grouped by state
    result = await db.execute(
        select(JobCard.state, func.count(JobCard.id))
        .filter(JobCard.tenant_id == tenant_id)
        .group_by(JobCard.state)
    )
    jobs_by_state = {state: count for state, count in result.all()}

    # Pending approvals
    result = await db.execute(
        select(func.count(JobCard.id)).filter(
            JobCard.tenant_id == tenant_id, JobCard.state == "APPROVAL_PENDING"
        )
    )
    pending_approvals = result.scalar() or 0

    # Total revenue from invoices
    result = await db.execute(
        select(func.sum(Invoice.total_amount)).filter(Invoice.tenant_id == tenant_id)
    )
    total_revenue = result.scalar() or 0.0
    gross_margin = round(total_revenue * 0.3, 2)

    return {
        "revenue": round(total_revenue, 2),
        "gross_margin": gross_margin,
        "jobs_by_state": jobs_by_state,
        "pending_approvals": pending_approvals,
    }


async def get_fleet_dashboard_data(db: AsyncSession, tenant_id: str) -> dict:
    result = await db.execute(
        select(func.count(JobCard.id)).filter(JobCard.tenant_id == tenant_id)
    )
    total_jobs = result.scalar() or 0
    return {
        "total_jobs": total_jobs,
        "mg_commitments_vs_actual_spend": {},
        "cost_per_vehicle": {},
        "downtime_metrics": {},
    }


async def get_owner_dashboard_data(db: AsyncSession, tenant_id: str, vehicle_id: int) -> dict:
    result = await db.execute(
        select(JobCard).filter(
            JobCard.tenant_id == tenant_id, JobCard.vehicle_id == vehicle_id
        ).order_by(JobCard.created_at.desc()).limit(10)
    )
    service_history = [
        {"id": jc.id, "job_no": jc.job_no, "state": jc.state, "complaint": jc.complaint}
        for jc in result.scalars().all()
    ]
    return {"vehicle_id": vehicle_id, "service_history": service_history, "upcoming_service_due": []}