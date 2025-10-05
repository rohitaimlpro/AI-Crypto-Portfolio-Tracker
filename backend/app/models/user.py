# app/models/user.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserBase(SQLModel):
    """Base user model with common fields"""
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    full_name: Optional[str] = Field(max_length=255, default=None)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    role: UserRole = Field(default=UserRole.USER)

class User(UserBase, table=True):
    """Database User model"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255)
    verification_token: Optional[str] = Field(max_length=255, default=None)
    reset_password_token: Optional[str] = Field(max_length=255, default=None)
    reset_password_expires: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Remove relationships for now to avoid circular imports
    # portfolios: List["Portfolio"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(min_length=8, max_length=100)

class UserResponse(UserBase):
    """Schema for user responses (excluding sensitive data)"""
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

class UserLogin(SQLModel):
    """Schema for user login"""
    email: str
    password: str

class TokenResponse(SQLModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserInDB(UserBase):
    """User model as stored in database (for internal use)"""
    id: int
    hashed_password: str
    created_at: datetime