# app/services/news_service.py
import httpx
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class NewsService:
    """Service for fetching cryptocurrency news"""
    
    def __init__(self):
        self.base_url = settings.NEWSAPI_BASE_URL
        self.api_key = settings.NEWSAPI_KEY
        self.timeout = 10.0
    
    async def get_coin_news(self, coin_name: str, limit: int = 5) -> List[Dict]:
        """Fetch latest news articles about a specific cryptocurrency"""
        try:
            # Calculate date range (last 7 days)
            from_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/everything"
            params = {
                "q": f"{coin_name} cryptocurrency",
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": limit,
                "apiKey": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                articles = data.get("articles", [])
                
                # Format articles
                formatted_articles = []
                for article in articles:
                    formatted_articles.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "source": article.get("source", {}).get("name"),
                        "published_at": article.get("publishedAt"),
                        "url": article.get("url")
                    })
                
                logger.info(f"Fetched {len(formatted_articles)} news articles for {coin_name}")
                return formatted_articles
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching news for {coin_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching news for {coin_name}: {e}")
            return []

news_service = NewsService()