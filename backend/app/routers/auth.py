# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import logging

from app.database import get_async_session
from app.services.auth import AuthService
from app.models.user import User, UserCreate, UserLogin, UserResponse, TokenResponse
from app.dependencies import get_current_user
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()
from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Register a new user
    """
    try:
        logger.info(f"Attempting to register user: {user_create.email}")
        
        user = await AuthService.create_user(session, user_create)
        logger.info(f"User registered successfully: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login
        )
    
    except HTTPException as e:
        logger.error(f"HTTP Exception during registration: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_login: UserLogin,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Login user and return JWT tokens
    """
    try:
        # Authenticate user
        user = await AuthService.authenticate_user(
            session, user_login.email, user_login.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            },
            expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.id, "email": user.email}
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/login/oauth", response_model=TokenResponse)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    """
    OAuth2 compatible login endpoint (for FastAPI docs)
    """
    try:
        user = await AuthService.authenticate_user(
            session, form_data.username, form_data.password  # OAuth2 uses username field for email
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            },
            expires_delta=access_token_expires
        )
        
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during OAuth login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

# Replace the existing refresh endpoint with this:
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Strip quotes that Swagger UI might add
        refresh_token = refresh_token.strip('"')
        
        logger.info(f"Received refresh token: {refresh_token[:50]}...")
        
        # Decode refresh token
        payload = AuthService.decode_token(refresh_token)
        logger.info(f"Token decoded successfully. Payload: {payload}")
        
        if payload.get("type") != "refresh":
            logger.error(f"Invalid token type: {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id_str = payload.get("sub")
        user_id = int(user_id_str)
        logger.info(f"Looking up user ID: {user_id}")
        
        user = await AuthService.get_user_by_id(session, user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"Refresh successful for user: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
    
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        role=current_user.role,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )