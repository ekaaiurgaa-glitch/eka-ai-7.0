"""Refresh Token Service - TDD Section 6.1"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import Base
import secrets


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    token = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    tenant_id = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


async def create_refresh_token(db: AsyncSession, user_id: str, tenant_id: str) -> str:
    """Create 7-day rotating refresh token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        tenant_id=tenant_id,
        expires_at=expires_at
    )
    db.add(refresh_token)
    await db.commit()
    return token


async def verify_refresh_token(db: AsyncSession, token: str) -> Optional[dict]:
    """Verify and rotate refresh token"""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
    )
    refresh_token = result.scalar_one_or_none()
    
    if not refresh_token:
        return None
    
    # Revoke old token
    refresh_token.revoked = True
    await db.commit()
    
    # Create new token (rotation)
    new_token = await create_refresh_token(db, refresh_token.user_id, refresh_token.tenant_id)
    
    return {
        "user_id": refresh_token.user_id,
        "tenant_id": refresh_token.tenant_id,
        "new_refresh_token": new_token
    }
