# app/services/ai_service.py
import logging
from typing import Dict, Optional, List
from datetime import datetime
import google.generativeai as genai

from app.config import get_settings
from app.services.news_service import news_service

logger = logging.getLogger(__name__)
settings = get_settings()
# At the top of the file, add after imports:
logger.info(f"NEWSAPI_KEY loaded: {bool(settings.NEWSAPI_KEY)}")
logger.info(f"GEMINI_API_KEY loaded: {bool(settings.GEMINI_API_KEY)}")
# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class AIService:
    """AI service for generating crypto insights using Gemini and real news"""
    
    def __init__(self):
        self.model = None
        if settings.GEMINI_API_KEY:
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("Gemini AI model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
    
    async def get_coin_insights(self, coin_id: str, coin_name: str, current_price: float) -> Dict:
        """Generate AI insights for a coin using real news and Gemini"""
        
        # Fetch recent news about the coin
        news_articles = await news_service.get_coin_news(coin_name, limit=5)
        
        if not self.model or not news_articles:
            # Fallback to placeholder if no API key or no news
            return self._get_placeholder_insights(coin_id, current_price)
        
        try:
            # Prepare prompt for Gemini
            news_text = "\n\n".join([
                f"- {article['title']}: {article['description']}"
                for article in news_articles if article['title']
            ])
            
            prompt = f"""
You are a cryptocurrency investment advisor. Analyze {coin_name} based on recent news and provide investment insights.

Current Price: ${current_price}

Recent News:
{news_text}

Provide a structured analysis with:
1. Brief summary (2-3 sentences)
2. Market sentiment (bullish/bearish/neutral)
3. 4 key points about the coin's current situation
4. Risk level (low/medium/high)
5. Investment recommendation (buy/hold/sell/research)

Format your response as JSON with these exact keys: summary, sentiment, key_points (array), risk_level, recommendation
"""
            
            response = self.model.generate_content(prompt)
            
            # Parse Gemini response
            try:
                import json
                # Try to extract JSON from response
                response_text = response.text
                
                # Simple parsing - looking for JSON structure
                if "{" in response_text:
                    json_start = response_text.index("{")
                    json_end = response_text.rindex("}") + 1
                    parsed = json.loads(response_text[json_start:json_end])
                    
                    return {
                        "coin_id": coin_id,
                        "coin_name": coin_name,
                        "current_price": current_price,
                        "generated_at": datetime.utcnow().isoformat(),
                        "summary": parsed.get("summary", ""),
                        "sentiment": parsed.get("sentiment", "neutral"),
                        "key_points": parsed.get("key_points", []),
                        "risk_level": parsed.get("risk_level", "medium"),
                        "recommendation": parsed.get("recommendation", "research"),
                        "news_sources": len(news_articles)
                    }
                else:
                    # If not JSON, parse as text
                    return self._parse_text_response(response_text, coin_id, coin_name, current_price, len(news_articles))
                    
            except Exception as e:
                logger.error(f"Error parsing Gemini response: {e}")
                return self._parse_text_response(response.text, coin_id, coin_name, current_price, len(news_articles))
                
        except Exception as e:
            logger.error(f"Error generating Gemini insights: {e}")
            return self._get_placeholder_insights(coin_id, current_price)
    
    def _parse_text_response(self, text: str, coin_id: str, coin_name: str, price: float, news_count: int) -> Dict:
        """Parse Gemini text response when JSON parsing fails"""
        return {
            "coin_id": coin_id,
            "coin_name": coin_name,
            "current_price": price,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": text[:300] + "..." if len(text) > 300 else text,
            "sentiment": "neutral",
            "key_points": text.split("\n")[:4],
            "risk_level": "medium",
            "recommendation": "research",
            "news_sources": news_count
        }
    
    def _get_placeholder_insights(self, coin_id: str, current_price: float) -> Dict:
        """Fallback placeholder insights"""
        return {
            "coin_id": coin_id,
            "current_price": current_price,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": f"Analysis for {coin_id} - API keys not configured",
            "sentiment": "neutral",
            "key_points": ["Configure API keys for real-time insights"],
            "risk_level": "medium",
            "recommendation": "research",
            "news_sources": 0
        }
    
    async def get_portfolio_analysis(self, portfolio_data: Dict) -> Dict:
        """Generate portfolio-level AI analysis"""
        # Keep the simple rule-based version for portfolio analysis
        total_value = portfolio_data.get("total_value", 0)
        holdings_count = portfolio_data.get("holdings_count", 0)
        
        diversification = "good" if holdings_count >= 5 else "low"
        risk_assessment = "high" if holdings_count < 3 else "medium"
        
        recommendations = []
        if holdings_count < 3:
            recommendations.append("Consider diversifying into more assets")
        if total_value < 1000:
            recommendations.append("Small portfolio - focus on major cryptocurrencies")
        
        return {
            "portfolio_id": portfolio_data.get("portfolio_id"),
            "total_value": total_value,
            "diversification": diversification,
            "risk_level": risk_assessment,
            "recommendations": recommendations if recommendations else ["Portfolio looks balanced"],
            "generated_at": datetime.utcnow().isoformat()
        }

ai_service = AIService()
