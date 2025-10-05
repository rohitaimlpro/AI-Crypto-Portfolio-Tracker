# app/models/transaction.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class Transaction(SQLModel, table=True):
    """Basic Transaction model - we'll expand this later"""
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    portfolio_id: int = Field(foreign_key="portfolios.id") 
    coin_id: str = Field(max_length=100)
    symbol: str = Field(max_length=20)
    transaction_type: TransactionType
    quantity: Decimal = Field(decimal_places=18, max_digits=36)
    price: Decimal = Field(decimal_places=8, max_digits=20)
    total_value: Decimal = Field(decimal_places=8, max_digits=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
