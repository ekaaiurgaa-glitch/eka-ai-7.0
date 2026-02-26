import asyncio
from sqlalchemy import select
from passlib.context import CryptContext
from app.db.session import AsyncSessionLocal
from app.db.models import User, Tenant, Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_user():
    async with AsyncSessionLocal() as session:
        # 1. Create a default tenant if not exists
        stmt = select(Tenant).where(Tenant.id == "tenant_admin")
        result = await session.execute(stmt)
        tenant = result.scalar_one_or_none()
        if not tenant:
            tenant = Tenant(
                id="tenant_admin",
                name="EKA Admin Workshop",
                type="workshop",
                city="Bengaluru",
                state="Karnataka"
            )
            session.add(tenant)

        # 2. Create the admin user
        stmt = select(User).where(User.email == "admin@eka.ai")
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                id="user_admin",
                tenant_id="tenant_admin",
                email="admin@eka.ai",
                hashed_password=pwd_context.hash("admin"),
                full_name="System Administrator",
                role_id="role_owner", # matches seeded role in migration 0017
                is_active=True
            )
            session.add(user)
        
        await session.commit()
    print("Default tenant and user seeded: admin@eka.ai / admin")

if __name__ == "__main__":
    asyncio.run(seed_user())
