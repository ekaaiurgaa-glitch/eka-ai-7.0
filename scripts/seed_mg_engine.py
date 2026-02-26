import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.modules.mg_engine.model import MGFormula, CityIndex
import os
from decimal import Decimal

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./eka_ai.db")

async def seed():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Seed Formulas
        for f in [
            {"make": "Tata", "model": "Nexon", "fuel_type": "diesel", "annual_base_cost_inr": Decimal("60000")},
            {"make": "Tata", "model": "Nexon", "variant": "XZ+", "fuel_type": "diesel", "annual_base_cost_inr": Decimal("72000")},
            {"make": "Maruti", "model": "Swift", "fuel_type": "petrol", "annual_base_cost_inr": Decimal("45000")},
        ]:
            try:
                session.add(MGFormula(**f, parts_pct=Decimal("60.0"), labor_pct=Decimal("40.0")))
                await session.flush()
            except:
                await session.rollback()
        
        # 2. Seed City Indices
        for c in [
            {"city": "Mumbai", "tier": "1", "multiplier": Decimal("1.15")},
            {"city": "Pune", "tier": "1", "multiplier": Decimal("1.05")},
            {"city": "Bangalore", "tier": "1", "multiplier": Decimal("1.10")},
        ]:
            try:
                session.add(CityIndex(**c))
                await session.flush()
            except:
                await session.rollback()
        
        await session.commit()
        print("MG Engine data seeding attempt complete.")

if __name__ == "__main__":
    asyncio.run(seed())
