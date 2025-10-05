# app/models/portfolio.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PortfolioBase(SQLModel):
    """Base portfolio model"""
    name: str = Field(max_length=255, default="My Portfolio")
    description: Optional[str] = Field(max_length=500, default=None)
    is_public: bool = Field(default=False)

class Portfolio(PortfolioBase, table=True):
    """Database Portfolio model"""
    __tablename__ = "portfolios"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Remove relationships for now to avoid SQLAlchemy configuration issues
    # user: "User" = Relationship(back_populates="portfolios")
    # holdings: List["PortfolioHolding"] = Relationship(back_populates="portfolio")

class PortfolioHoldingBase(SQLModel):
    """Base portfolio holding model"""
    coin_id: str = Field(max_length=100)  # CoinGecko coin ID (e.g., 'bitcoin')
    symbol: str = Field(max_length=20)    # Coin symbol (e.g., 'BTC')
    quantity: Decimal = Field(default=0)
    average_buy_price: Optional[Decimal] = Field(default=None)

class PortfolioHolding(PortfolioHoldingBase, table=True):
    """Database PortfolioHolding model"""
    __tablename__ = "portfolio_holdings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolios.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Remove relationship for now
    # portfolio: Portfolio = Relationship(back_populates="holdings")

# Response Schemas
class PortfolioCreate(PortfolioBase):
    """Schema for creating a new portfolio"""
    pass

class PortfolioResponse(PortfolioBase):
    """Schema for portfolio response"""
    id: int
    user_id: int
    total_value: Optional[Decimal] = None
    holdings_count: int = 0
    created_at: datetime