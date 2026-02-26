"""Initialize the database with all tables and seed data."""
import asyncio
from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.db import models
from app.modules.catalog.model import Part, LaborRate
from app.modules.vehicles.model import Vehicle


async def init_db():
    print("Creating database tables...")
    async with engine.begin() as conn:
        # Enable pgvector extension if PostgreSQL
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("pgvector extension enabled")
        except Exception:
            print("pgvector not available (SQLite mode)")
        
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created!")

    print("Seeding catalog data...")
    async with AsyncSessionLocal() as session:
        # Seed parts
        parts = [
            Part(tenant_id="tenant_admin", part_number="BRK-001", description="Brake Pad Set", hsn_code="8708", unit_price=1500.0, gst_rate=18.0),
            Part(tenant_id="tenant_admin", part_number="OIL-001", description="Engine Oil 5W-30", hsn_code="2710", unit_price=450.0, gst_rate=18.0),
            Part(tenant_id="tenant_admin", part_number="FLT-001", description="Oil Filter", hsn_code="8421", unit_price=250.0, gst_rate=18.0),
            Part(tenant_id="tenant_admin", part_number="BAT-001", description="Car Battery 12V", hsn_code="8507", unit_price=4500.0, gst_rate=28.0),
            Part(tenant_id="tenant_admin", part_number="TYR-001", description="Tyre 185/65 R15", hsn_code="4011", unit_price=3500.0, gst_rate=28.0),
        ]
        session.add_all(parts)

        # Seed labor rates
        labor_rates = [
            LaborRate(tenant_id="tenant_admin", service_type="general_service", city="default", rate_per_hour=400.0, estimated_hours=1.0),
            LaborRate(tenant_id="tenant_admin", service_type="brake_service", city="default", rate_per_hour=500.0, estimated_hours=2.0),
            LaborRate(tenant_id="tenant_admin", service_type="engine_overhaul", city="default", rate_per_hour=800.0, estimated_hours=8.0),
        ]
        session.add_all(labor_rates)

        await session.commit()
    print("Seed data added successfully!")
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
