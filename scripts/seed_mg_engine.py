import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.modules.mg_engine.model import MGFormula, CityIndex
import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./eka_ai.db")

async def seed():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Comprehensive MG Formulas with Variants
        formulas = [
            {"make": "Tata", "model": "Nexon", "variant": "XE", "fuel_type": "diesel", "annual_base_cost_inr": Decimal("58000")},
            {"make": "Tata", "model": "Nexon", "variant": "XM", "fuel_type": "diesel", "annual_base_cost_inr": Decimal("62000")},
            {"make": "Tata", "model": "Nexon", "variant": "XZ+", "fuel_type": "diesel", "annual_base_cost_inr": Decimal("72000")},
            {"make": "Tata", "model": "Nexon", "variant": "XE", "fuel_type": "petrol", "annual_base_cost_inr": Decimal("52000")},
            {"make": "Maruti", "model": "Swift", "variant": "LXI", "fuel_type": "petrol", "annual_base_cost_inr": Decimal("42000")},
            {"make": "Maruti", "model": "Swift", "variant": "VXI", "fuel_type": "petrol", "annual_base_cost_inr": Decimal("48000")},
            {"make": "Maruti", "model": "Swift", "variant": "ZXI", "fuel_type": "petrol", "annual_base_cost_inr": Decimal("54000")},
            {"make": "Hyundai", "model": "Creta", "variant": "E", "fuel_type": "petrol", "annual_base_cost_inr": Decimal("65000")},
            {"make": "Hyundai", "model": "Creta", "variant": "SX", "fuel_type": "diesel", "annual_base_cost_inr": Decimal("78000")},
            {"make": "Mahindra", "model": "Scorpio", "variant": "S11", "fuel_type": "diesel", "annual_base_cost_inr": Decimal("85000")},
        ]
        
        for f in formulas:
            try:
                session.add(MGFormula(**f, parts_pct=Decimal("65.0"), labor_pct=Decimal("35.0")))
                await session.flush()
            except Exception as e:
                await session.rollback()
                print(f"Formula exists or error: {f['make']} {f['model']} {f.get('variant', '')}")
        
        # 2. Comprehensive City Indices
        cities = [
            {"city": "Mumbai", "tier": "1", "multiplier": Decimal("1.15")},
            {"city": "Delhi", "tier": "1", "multiplier": Decimal("1.12")},
            {"city": "Bangalore", "tier": "1", "multiplier": Decimal("1.10")},
            {"city": "Pune", "tier": "1", "multiplier": Decimal("1.05")},
            {"city": "Hyderabad", "tier": "1", "multiplier": Decimal("1.08")},
            {"city": "Chennai", "tier": "1", "multiplier": Decimal("1.07")},
            {"city": "Kolkata", "tier": "1", "multiplier": Decimal("1.06")},
            {"city": "Ahmedabad", "tier": "2", "multiplier": Decimal("1.02")},
            {"city": "Jaipur", "tier": "2", "multiplier": Decimal("1.00")},
            {"city": "Lucknow", "tier": "2", "multiplier": Decimal("0.98")},
            {"city": "Indore", "tier": "2", "multiplier": Decimal("0.97")},
            {"city": "Nagpur", "tier": "3", "multiplier": Decimal("0.95")},
        ]
        
        for c in cities:
            try:
                session.add(CityIndex(**c))
                await session.flush()
            except Exception as e:
                await session.rollback()
                print(f"City exists: {c['city']}")
        
        await session.commit()
        print(f"[OK] MG Engine seeding complete: {len(formulas)} formulas, {len(cities)} cities")

if __name__ == "__main__":
    asyncio.run(seed())
