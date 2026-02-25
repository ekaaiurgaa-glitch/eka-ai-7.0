from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user
from typing import List, Union

def require_role(roles: Union[str, List[str]]):
    """
    Dependency that enforces one of the specified roles.
    Usage: Depends(require_role(["manager", "owner"]))
    """
    if isinstance(roles, str):
        roles = [roles]
        
    async def _check(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(roles)}",
            )
        return user
    return _check
