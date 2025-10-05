# app/services/coingecko.py
import httpx
import logging
from typing import Optional, Dict, List
from decimal import Decimal
import asyncio

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class CoinGeckoService:
    """Service for interacting with CoinGecko API"""
    
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.api_key = settings.COINGECKO_API_KEY
        self.timeout = 10.0
    
    async def get_coin_price(self, coin_id: str, vs_currency: str = "usd") -> Optional[Decimal]:
        """Get current price of a coin"""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": vs_currency
            }
            
            if self.api_key:
                params["x_cg_pro_api_key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if coin_id in data and vs_currency in data[coin_id]:
                    price = Decimal(str(data[coin_id][vs_currency]))
                    logger.info(f"Fetched price for {coin_id}: ${price}")
                    return price
                
                logger.warning(f"No price data found for {coin_id}")
                return None
                
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching price for {coin_id}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching price for {coin_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching price for {coin_id}: {e}")
            return None
    
    async def get_multiple_prices(
        self, 
        coin_ids: List[str], 
        vs_currency: str = "usd"
    ) -> Dict[str, Decimal]:
        """Get prices for multiple coins at once"""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": vs_currency
            }
            
            if self.api_key:
                params["x_cg_pro_api_key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                prices = {}
                for coin_id in coin_ids:
                    if coin_id in data and vs_currency in data[coin_id]:
                        prices[coin_id] = Decimal(str(data[coin_id][vs_currency]))
                
                logger.info(f"Fetched prices for {len(prices)} coins")
                return prices
                
        except Exception as e:
            logger.error(f"Error fetching multiple prices: {e}")
            return {}
    
    async def get_coin_details(self, coin_id: str) -> Optional[Dict]:
        """Get detailed information about a coin"""
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false"
            }
            
            if self.api_key:
                params["x_cg_pro_api_key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract relevant data
                coin_data = {
                    "id": data.get("id"),
                    "symbol": data.get("symbol", "").upper(),
                    "name": data.get("name"),
                    "current_price": data.get("market_data", {}).get("current_price", {}).get("usd"),
                    "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                    "price_change_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
                    "image": data.get("image", {}).get("small")
                }
                
                logger.info(f"Fetched details for {coin_id}")
                return coin_data
                
        except Exception as e:
            logger.error(f"Error fetching coin details for {coin_id}: {e}")
            return None
    
    async def search_coins(self, query: str) -> List[Dict]:
        """Search for coins by name or symbol"""
        try:
            url = f"{self.base_url}/search"
            params = {"query": query}
            
            if self.api_key:
                params["x_cg_pro_api_key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                coins = data.get("coins", [])
                
                # Return simplified results
                results = [
                    {
                        "id": coin.get("id"),
                        "name": coin.get("name"),
                        "symbol": coin.get("symbol", "").upper(),
                        "thumb": coin.get("thumb")
                    }
                    for coin in coins[:10]  # Limit to top 10 results
                ]
                
                logger.info(f"Found {len(results)} coins for query: {query}")
                return results
                
        except Exception as e:
            logger.error(f"Error searching coins: {e}")
            return []

# Singleton instance
coingecko_service = CoinGeckoService()
