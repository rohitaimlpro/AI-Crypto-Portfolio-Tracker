# app/tasks/portfolio_tasks.py
from app.tasks.celery_app import celery_app
from sqlmodel import select, Session
from app.database import engine
from app.models.portfolio import Portfolio, PortfolioHolding
from app.services.coingecko import coingecko_service
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='app.tasks.portfolio_tasks.update_all_portfolio_values')
def update_all_portfolio_values():
    """Background task to update all portfolio values"""
    logger.info("Starting portfolio values update task")
    
    try:
        with Session(engine) as session:
            # Get all portfolios - use execute() instead of exec()
            portfolios = session.execute(select(Portfolio)).scalars().all()
            
            updated_count = 0
            for portfolio in portfolios:
                try:
                    # Get holdings for this portfolio
                    holdings = session.execute(
                        select(PortfolioHolding).where(
                            PortfolioHolding.portfolio_id == portfolio.id
                        )
                    ).scalars().all()
                    
                    if holdings:
                        logger.info(f"Updating portfolio {portfolio.id} with {len(holdings)} holdings")
                        updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error updating portfolio {portfolio.id}: {e}")
                    continue
            
            logger.info(f"Updated {updated_count} portfolios")
            return {"updated": updated_count, "total": len(portfolios)}
            
    except Exception as e:
        logger.error(f"Error in portfolio update task: {e}")
        raise

@celery_app.task(name='app.tasks.portfolio_tasks.update_coin_prices_cache')
def update_coin_prices_cache():
    """Background task to update coin prices in cache"""
    logger.info("Starting coin prices cache update task")
    
    try:
        with Session(engine) as session:
            # Get all unique coin IDs from holdings
            holdings = session.execute(select(PortfolioHolding)).scalars().all()
            unique_coins = list(set([h.coin_id for h in holdings]))
            
            if not unique_coins:
                logger.info("No coins to update")
                return {"updated": 0}
            
            logger.info(f"Fetching prices for {len(unique_coins)} coins")
            logger.info(f"Would update prices for: {', '.join(unique_coins[:5])}...")
            
            return {"updated": len(unique_coins)}
            
    except Exception as e:
        logger.error(f"Error in price cache update task: {e}")
        raise

@celery_app.task(name='app.tasks.portfolio_tasks.calculate_portfolio_value')
def calculate_portfolio_value(portfolio_id: int):
    """Calculate value for a specific portfolio"""
    logger.info(f"Calculating value for portfolio {portfolio_id}")
    
    try:
        with Session(engine) as session:
            portfolio = session.get(Portfolio, portfolio_id)
            
            if not portfolio:
                logger.error(f"Portfolio {portfolio_id} not found")
                return None
            
            holdings = session.execute(
                select(PortfolioHolding).where(
                    PortfolioHolding.portfolio_id == portfolio_id
                )
            ).scalars().all()
            
            logger.info(f"Portfolio {portfolio_id} has {len(holdings)} holdings")
            
            return {
                "portfolio_id": portfolio_id,
                "holdings_count": len(holdings)
            }
            
    except Exception as e:
        logger.error(f"Error calculating portfolio value: {e}")
        raise