# app/routers/coins.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging

from app.services.coingecko import coingecko_service
from app.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search")
async def search_coins(
    query: str,
    current_user: User = Depends(get_current_user)
):
    """Search for coins by name or symbol"""
    if len(query) < 2:
        raise HTTPException(
            status_code=400,
            detail="Query must be at least 2 characters"
        )
    
    results = await coingecko_service.search_coins(query)
    return {"results": results}

@router.get("/{coin_id}/price")
async def get_coin_price(
    coin_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get current price of a specific coin"""
    price = await coingecko_service.get_coin_price(coin_id)
    
    if price is None:
        raise HTTPException(
            status_code=404,
            detail=f"Price not found for coin: {coin_id}"
        )
    
    return {
        "coin_id": coin_id,
        "price_usd": float(price),
        "currency": "usd"
    }

@router.get("/{coin_id}/details")
async def get_coin_details(
    coin_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a coin"""
    details = await coingecko_service.get_coin_details(coin_id)
    
    if details is None:
        raise HTTPException(
            status_code=404,
            detail=f"Details not found for coin: {coin_id}"
        )
    
    return details