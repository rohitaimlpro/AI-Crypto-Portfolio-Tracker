# app/dependencies.py
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.services.auth import AuthService
from app.models.user import User

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Dependency to get the current authenticated user
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Get user info from token
    token_data = AuthService.get_current_user_from_token(token)
    
    # Get user from database
    user = await AuthService.get_user_by_id(session, token_data["user_id"])
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current admin user
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Optional authentication (for endpoints that work with or without auth)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_async_session)
) -> Optional[User]:
    """
    Optional authentication dependency - returns None if no token provided
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        token_data = AuthService.get_current_user_from_token(token)
        user = await AuthService.get_user_by_id(session, token_data["user_id"])
        
        if user and user.is_active:
            return user
    except HTTPException:
        # If token is invalid, return None instead of raising error
        pass
    
    return None
