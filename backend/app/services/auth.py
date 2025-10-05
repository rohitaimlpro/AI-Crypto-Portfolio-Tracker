# app/services/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging
import hashlib

from app.config import get_settings
from app.models.user import User, UserCreate

logger = logging.getLogger(__name__)
settings = get_settings()

class AuthService:
    """Authentication service for user management and JWT tokens"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash using bcrypt directly"""
        try:
            logger.info(f"Verifying password. Plain: '{plain_password}', Hash starts with: '{hashed_password[:20]}...'")
        
            # Convert strings to bytes
            plain_password_bytes = plain_password.encode('utf-8')
            hashed_password_bytes = hashed_password.encode('utf-8')
        
            # Use bcrypt directly
            result = bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
            logger.info(f"Password verification result: {result}")
            return result
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password using bcrypt directly"""
        try:
            # Convert to bytes and hash
            password_bytes = password.encode('utf-8')
            
            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password_bytes, salt)
            
            # Return as string
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            # Fallback to simple hash if bcrypt fails
            return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
    
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
    
    # Convert sub to string if it's an integer
        if "sub" in to_encode and isinstance(to_encode["sub"], int):
            to_encode["sub"] = str(to_encode["sub"])
    
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
    
    # Convert sub to string if it's an integer
        if "sub" in to_encode and isinstance(to_encode["sub"], int):
            to_encode["sub"] = str(to_encode["sub"])
    
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT decode error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            statement = select(User).where(User.email == email)
            result = await session.execute(statement)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            statement = select(User).where(User.username == username)
            result = await session.execute(statement)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            statement = select(User).where(User.id == user_id)
            result = await session.execute(statement)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await AuthService.get_user_by_email(session, email)
        
        if not user:
            logger.warning(f"Authentication failed: user not found for email {email}")
            return None
            
        if not user.is_active:
            logger.warning(f"Authentication failed: user {email} is not active")
            return None
            
        if not AuthService.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for email {email}")
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        session.add(user)
        await session.commit()
        
        logger.info(f"User {email} authenticated successfully")
        return user
    
    @staticmethod
    async def create_user(session: AsyncSession, user_create: UserCreate) -> User:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_email = await AuthService.get_user_by_email(session, user_create.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            existing_username = await AuthService.get_user_by_username(session, user_create.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            
            # Create user with hashed password
            logger.info(f"Hashing password for user: {user_create.email}")
            hashed_password = AuthService.get_password_hash(user_create.password)
            logger.info("Password hashed successfully")
            
            user_data = user_create.dict(exclude={"password"})
            
            user = User(
                **user_data,
                hashed_password=hashed_password
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            logger.info(f"New user created: {user.email}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User creation failed: {str(e)}"
            )
    
    @staticmethod
    def get_current_user_from_token(token: str) -> dict:
        """Extract user info from token"""
        payload = AuthService.decode_token(token)
    
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
        # Convert string back to int
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
        return {"user_id": user_id, "email": payload.get("email")}