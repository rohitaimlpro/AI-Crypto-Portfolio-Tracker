# app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import auth, portfolio, coins, ai_insights

# from app.routers import users, coins

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Crypto Portfolio Tracker API")
    await init_db()  # Initialize database tables
    yield
    # Shutdown
    logger.info("🛑 Shutting down Crypto Portfolio Tracker API")

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Crypto Portfolio Tracker",
    description="A full-stack application for tracking crypto portfolios with AI insights",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - allowing frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(coins.router, prefix="/api/coins", tags=["Coins"])
app.include_router(ai_insights.router, prefix="/api/ai", tags=["AI Insights"])
# app.include_router(users.router, prefix="/api/users", tags=["Users"])

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "AI-Powered Crypto Portfolio Tracker API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "crypto-portfolio-api",
        "timestamp": time.time()
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with logging"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)