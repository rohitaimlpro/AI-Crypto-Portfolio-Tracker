# app/database.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging
from typing import AsyncGenerator

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create sync engine for Alembic migrations
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async engine for FastAPI
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Session factory for async operations
async_session_factory = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Initialize database tables"""
    try:
        logger.info("🔄 Starting database initialization...")
        
        # Import all models to ensure they're registered with SQLModel
        from app.models import user, portfolio  # Remove transaction, coin for now
        logger.info("📦 Models imported successfully")
        
        async with async_engine.begin() as conn:
            logger.info("🔌 Connected to database, creating tables...")
            await conn.run_sync(SQLModel.metadata.create_all)
            
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session"""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

def get_sync_session():
    """Get synchronous session (for Alembic migrations)"""
    with Session(engine) as session:
        yield session

# Health check function
async def check_database_health() -> bool:
    """Check if database is healthy"""
    try:
        async with async_session_factory() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False