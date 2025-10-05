# app/models/__init__.py
"""
Database models for the Crypto Portfolio Tracker
"""

# Import only the models that exist and work
from .user import User, UserCreate, UserResponse, UserLogin, TokenResponse, UserRole
from .portfolio import Portfolio, PortfolioHolding, PortfolioCreate, PortfolioResponse

# Don't import Transaction and Coin for now since they're empty

__all__ = [
    # User models
    "User",
    "UserCreate", 
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    "UserRole",
    
    # Portfolio models
    "Portfolio",
    "PortfolioHolding",
    "PortfolioCreate",
    "PortfolioResponse",
]