# app/routers/portfolio.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.database import get_async_session
from app.models.user import User
from app.models.portfolio import (
    Portfolio, 
    PortfolioCreate, 
    PortfolioResponse,
    PortfolioHolding,
    PortfolioHoldingBase
)
from app.dependencies import get_current_user
from sqlmodel import select

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new portfolio for the current user"""
    try:
        portfolio = Portfolio(
            **portfolio_data.dict(),
            user_id=current_user.id
        )
        
        session.add(portfolio)
        await session.commit()
        await session.refresh(portfolio)
        
        logger.info(f"Portfolio created: {portfolio.id} for user {current_user.email}")
        
        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            is_public=portfolio.is_public,
            user_id=portfolio.user_id,
            created_at=portfolio.created_at,
            holdings_count=0
        )
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create portfolio"
        )

@router.get("/", response_model=List[PortfolioResponse])
async def get_user_portfolios(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get all portfolios for the current user"""
    try:
        statement = select(Portfolio).where(Portfolio.user_id == current_user.id)
        result = await session.execute(statement)
        portfolios = result.scalars().all()
        
        response = []
        for portfolio in portfolios:
            # Count holdings
            holdings_statement = select(PortfolioHolding).where(
                PortfolioHolding.portfolio_id == portfolio.id
            )
            holdings_result = await session.execute(holdings_statement)
            holdings_count = len(holdings_result.scalars().all())
            
            response.append(PortfolioResponse(
                id=portfolio.id,
                name=portfolio.name,
                description=portfolio.description,
                is_public=portfolio.is_public,
                user_id=portfolio.user_id,
                created_at=portfolio.created_at,
                holdings_count=holdings_count
            ))
        
        return response
    except Exception as e:
        logger.error(f"Error getting portfolios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolios"
        )

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific portfolio by ID"""
    try:
        statement = select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        result = await session.execute(statement)
        portfolio = result.scalars().first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        # Get holdings count
        holdings_statement = select(PortfolioHolding).where(
            PortfolioHolding.portfolio_id == portfolio.id
        )
        holdings_result = await session.execute(holdings_statement)
        holdings_count = len(holdings_result.scalars().all())
        
        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            is_public=portfolio.is_public,
            user_id=portfolio.user_id,
            created_at=portfolio.created_at,
            holdings_count=holdings_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get portfolio"
        )
@router.post("/{portfolio_id}/holdings", status_code=status.HTTP_201_CREATED)
async def add_holding_to_portfolio(
    portfolio_id: int,
    holding_data: PortfolioHoldingBase,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Add a coin holding to a portfolio"""
    try:
        # Verify portfolio belongs to user
        portfolio_statement = select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        portfolio_result = await session.execute(portfolio_statement)
        portfolio = portfolio_result.scalars().first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        # Check if holding already exists
        existing_statement = select(PortfolioHolding).where(
            PortfolioHolding.portfolio_id == portfolio_id,
            PortfolioHolding.coin_id == holding_data.coin_id
        )
        existing_result = await session.execute(existing_statement)
        existing_holding = existing_result.scalars().first()
        
        if existing_holding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coin already exists in portfolio. Use update endpoint instead."
            )
        
        # Create new holding
        holding = PortfolioHolding(
            portfolio_id=portfolio_id,
            **holding_data.dict()
        )
        
        session.add(holding)
        await session.commit()
        await session.refresh(holding)
        
        logger.info(f"Added holding {holding_data.coin_id} to portfolio {portfolio_id}")
        
        return {
            "message": "Holding added successfully",
            "holding_id": holding.id,
            "coin_id": holding.coin_id,
            "quantity": holding.quantity
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding holding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add holding"
        )

@router.get("/{portfolio_id}/holdings")
async def get_portfolio_holdings(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get all holdings in a portfolio"""
    try:
        # Verify portfolio belongs to user
        portfolio_statement = select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        portfolio_result = await session.execute(portfolio_statement)
        portfolio = portfolio_result.scalars().first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        # Get all holdings
        holdings_statement = select(PortfolioHolding).where(
            PortfolioHolding.portfolio_id == portfolio_id
        )
        holdings_result = await session.execute(holdings_statement)
        holdings = holdings_result.scalars().all()
        
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "holdings": [
                {
                    "id": h.id,
                    "coin_id": h.coin_id,
                    "symbol": h.symbol,
                    "quantity": h.quantity,
                    "average_buy_price": h.average_buy_price,
                    "created_at": h.created_at
                }
                for h in holdings
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting holdings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get holdings"
        )
@router.get("/{portfolio_id}/valuation")
async def get_portfolio_valuation(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Calculate total portfolio value using current prices"""
    from app.services.coingecko import coingecko_service
    from decimal import Decimal
    
    try:
        # Verify portfolio belongs to user
        portfolio_statement = select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
        portfolio_result = await session.execute(portfolio_statement)
        portfolio = portfolio_result.scalars().first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        # Get all holdings
        holdings_statement = select(PortfolioHolding).where(
            PortfolioHolding.portfolio_id == portfolio_id
        )
        holdings_result = await session.execute(holdings_statement)
        holdings = holdings_result.scalars().all()
        
        if not holdings:
            return {
                "portfolio_id": portfolio_id,
                "portfolio_name": portfolio.name,
                "total_value_usd": 0,
                "holdings": []
            }
        
        # Get all coin IDs
        coin_ids = [h.coin_id for h in holdings]
        
        # Fetch current prices
        prices = await coingecko_service.get_multiple_prices(coin_ids)
        
        # Calculate values
        total_value = Decimal("0")
        holdings_data = []
        
        for holding in holdings:
            current_price = prices.get(holding.coin_id, Decimal("0"))
            holding_value = current_price * holding.quantity
            total_value += holding_value
            
            profit_loss = None
            if holding.average_buy_price:
                cost_basis = holding.average_buy_price * holding.quantity
                profit_loss = float(holding_value - cost_basis)
            
            holdings_data.append({
                "coin_id": holding.coin_id,
                "symbol": holding.symbol,
                "quantity": float(holding.quantity),
                "current_price": float(current_price),
                "holding_value": float(holding_value),
                "average_buy_price": float(holding.average_buy_price) if holding.average_buy_price else None,
                "profit_loss": profit_loss
            })
        
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "total_value_usd": float(total_value),
            "holdings": holdings_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating portfolio valuation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate portfolio valuation"
        )
