# app/models/coin.py  
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Coin(SQLModel, table=True):
    """Basic Coin model for caching coin data"""
    __tablename__ = "coins"
    
    id: str = Field(primary_key=True, max_length=100)  # CoinGecko ID
    symbol: str = Field(max_length=20)
    name: str = Field(max_length=255)
    current_price: Optional[Decimal] = Field(decimal_places=8, max_digits=20, default=None)
    market_cap: Optional[Decimal] = Field(decimal_places=2, max_digits=20, default=None)
    price_change_24h: Optional[Decimal] = Field(decimal_places=8, max_digits=20, default=None)
    last_updated: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
