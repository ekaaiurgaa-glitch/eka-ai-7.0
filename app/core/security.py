from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

# This is a placeholder for the actual token verification logic.
# In a real application, you would use a library like python-jose to decode and verify the JWT.
def verify_token(token: str):
    if token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"sub": "user@example.com", "permissions": ["chat_access", "can_create_invoice"]}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    return user

def has_permission(user: dict, permission: str):
    return permission in user.get("permissions", [])

async def get_current_user_with_permission(permission: str, user: dict = Depends(get_current_user)):
    if not has_permission(user, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have the required permission",
        )
    return user
