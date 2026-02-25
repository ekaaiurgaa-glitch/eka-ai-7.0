"""Auth Router with Refresh Token - TDD Section 6.1"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.core.refresh_token import create_refresh_token, verify_refresh_token
from app.core.security import create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    TDD Section 6.1: 7-day rotating refresh tokens
    Revokes old token and issues new access + refresh token pair
    """
    result = await verify_refresh_token(db, request.refresh_token)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    # Create new access token
    access_token = create_access_token(
        data={
            "sub": result["user_id"],
            "tenant_id": result["tenant_id"]
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=result["new_refresh_token"]
    )
