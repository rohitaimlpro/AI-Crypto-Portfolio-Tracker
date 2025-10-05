# app/routers/ai_insights.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.services.ai_service import ai_service
from app.services.coingecko import coingecko_service
from app.dependencies import get_current_user
from app.models.user import User
from app.database import get_async_session
from app.models.portfolio import Portfolio, PortfolioHolding
from sqlmodel import select
from decimal import Decimal

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{coin_id}")
async def get_coin_ai_insights(
    coin_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated insights for a specific coin based on real news"""
    try:
        # Get current price and coin details
        price = await coingecko_service.get_coin_price(coin_id)
        coin_details = await coingecko_service.get_coin_details(coin_id)
        
        if price is None:
            raise HTTPException(status_code=404, detail="Coin not found")
        
        coin_name = coin_details.get("name", coin_id) if coin_details else coin_id
        
        # Get AI insights with real news
        insights = await ai_service.get_coin_insights(coin_id, coin_name, float(price))
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")

@router.get("/portfolio/{portfolio_id}")
async def get_portfolio_ai_analysis(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get AI analysis for a portfolio"""
    try:
        # Verify portfolio belongs to user
        portfolio_statement = select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        portfolio_result = await session.execute(portfolio_statement)
        portfolio = portfolio_result.scalars().first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get holdings count
        holdings_statement = select(PortfolioHolding).where(
            PortfolioHolding.portfolio_id == portfolio_id
        )
        holdings_result = await session.execute(holdings_statement)
        holdings = holdings_result.scalars().all()
        
        # Get portfolio value
        coin_ids = [h.coin_id for h in holdings]
        prices = await coingecko_service.get_multiple_prices(coin_ids)
        
        total_value = Decimal("0")
        for holding in holdings:
            price = prices.get(holding.coin_id, Decimal("0"))
            total_value += price * holding.quantity
        
        portfolio_data = {
            "portfolio_id": portfolio_id,
            "total_value": float(total_value),
            "holdings_count": len(holdings)
        }
        
        # Get AI analysis
        analysis = await ai_service.get_portfolio_analysis(portfolio_data)
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate analysis")
