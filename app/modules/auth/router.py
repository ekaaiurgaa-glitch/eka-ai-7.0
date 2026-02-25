from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.db.models import User, Role
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    role: str
    tenant_id: str

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password (P1-1).
    """
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Get role permissions
    stmt = select(Role).where(Role.id == user.role_id)
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    permissions = role.permissions if role else []

    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "role": role.name if role else "customer",
        "permissions": permissions
    }
    
    token = create_access_token(token_data)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": role.name if role else "customer",
        "tenant_id": user.tenant_id
    }

@router.get("/me")
async def get_me(user: User = Depends(get_db)):
    # This is a placeholder
    return {"status": "active"}
