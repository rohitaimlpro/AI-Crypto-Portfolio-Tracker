# test_db.py
import asyncio
import sys
import os
sys.path.append(os.getcwd())

from sqlmodel import SQLModel, create_engine
from app.config import get_settings
from app.models import User, Portfolio, PortfolioHolding  # Only import these for now

async def test_database():
    settings = get_settings()
    print(f"🔗 Database URL: {settings.DATABASE_URL}")
    
    try:
        # Create sync engine for testing
        engine = create_engine(settings.DATABASE_URL, echo=True)
        print("✅ Database connection successful")
        
        # Create tables
        print("🔄 Creating tables...")
        SQLModel.metadata.create_all(engine)
        print("✅ Tables created successfully")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print(f"✅ Query test successful: {result.fetchone()}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())