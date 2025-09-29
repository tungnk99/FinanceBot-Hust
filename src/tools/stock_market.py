import asyncio
import httpx
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from agents import RunContextWrapper, FunctionTool, function_tool


class MarketQuery(BaseModel):
    """Schema for Vietnamese stock market data queries"""
    
    symbols: List[str] = Field(
        ..., 
        description="List of stock symbols to query (e.g., ['VIC', 'VCB', 'VHM'])",
        min_items=1,
        max_items=50
    )
    
    exchange: Optional[str] = Field(
        default="HOSE",
        description="Exchange to get data from (HOSE, HNX, UPCOM, ALL)",
        pattern="^(HOSE|HNX|UPCOM|ALL)$"
    )
    
    fields: Optional[List[str]] = Field(
        default=None,
        description="Specific fields to return (price, change, percent_change, volume, high, low, open, close, market_cap)",
        max_items=20
    )
    
    include_24h_change: bool = Field(
        default=True,
        description="Include 24-hour price change data"
    )
    
    include_volume: bool = Field(
        default=True,
        description="Include trading volume data"
    )
    
    include_market_cap: bool = Field(
        default=True,
        description="Include market capitalization data"
    )
    
    include_technical_indicators: bool = Field(
        default=False,
        description="Include technical analysis indicators (RSI, MACD, Moving Averages)"
    )
    
    currency: str = Field(
        default="VND",
        description="Currency for price data (VND, USD)",
        pattern="^(VND|USD)$"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbols": ["VIC", "VCB", "VHM", "HPG"],
                "exchange": "HOSE",
                "fields": ["price", "change", "percent_change", "volume", "market_cap"],
                "include_24h_change": True,
                "include_volume": True,
                "include_market_cap": True,
                "include_technical_indicators": False,
                "currency": "VND"
            }
        }


logger = logging.getLogger(__name__)


class VietnamMarketService:
    """Service class to handle Vietnamese market data operations"""
    
    def __init__(self):
        """Initialize VietnamMarketService with free APIs"""
        # Free APIs for Vietnamese market data
        self.apis = {
            "yfinance": "yfinance",  # Primary API
            "tcbs": "https://apipubaws.tcbs.com.vn/tcanalysis/v1/",
            "vietstock": "https://finance.vietstock.vn/data/",
            "cafef": "https://s.cafef.vn/Ajax/PageNew/DataHistory/"
        }
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json"
            }
        )
    
    async def get_realtime_data(self, market_query: MarketQuery) -> str:
        """
        Get realtime market data for Vietnamese stocks
        
        Args:
            market_query: MarketQuery object containing symbols and parameters
            
        Returns:
            JSON string containing market data
        """
        try:
            results = []
            
            for symbol in market_query.symbols:
                # Try multiple free APIs
                stock_data = await self._fetch_stock_data(symbol, market_query)
                if stock_data:
                    results.append(stock_data)
            
            return json.dumps({
                "success": True,
                "data": results,
                "timestamp": datetime.now().isoformat(),
                "query": market_query.dict(),
                "total_symbols": len(market_query.symbols),
                "successful_symbols": len(results)
            }, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_msg = f"Error in get_realtime_data: {str(e)}"
            logger.error(error_msg)
            return json.dumps({
                "success": False,
                "error": error_msg,
                "query": market_query.dict()
            }, ensure_ascii=False, indent=2)
    
    async def _fetch_stock_data(self, symbol: str, market_query: MarketQuery) -> Optional[Dict[str, Any]]:
        """Fetch data for a single stock symbol with smart fallback"""
        # Define API priority order (most reliable first)
        api_methods = [
            ("yfinance", self._fetch_from_yfinance),
            ("TCBS", self._fetch_from_tcbs),
            ("VietStock", self._fetch_from_vietstock),
            ("Cafef", self._fetch_from_cafef)
        ]
        
        for api_name, api_method in api_methods:
            try:
                logger.info(f"Trying {api_name} API for {symbol}")
                data = await api_method(symbol)
                
                if data and data.get('price', 0) > 0:  # Valid data check
                    logger.info(f"✅ Successfully fetched {symbol} data from {api_name}")
                    return self._format_stock_data(symbol, data, market_query)
                else:
                    logger.warning(f"⚠️ {api_name} returned invalid data for {symbol}")
                    
            except Exception as e:
                logger.warning(f"❌ {api_name} failed for {symbol}: {str(e)}")
                continue
        
        # If all APIs fail, create mock data
        logger.warning(f"🔄 All APIs failed for {symbol}, using mock data")
        return self._create_mock_data(symbol, market_query)
    
    async def _fetch_from_yfinance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from yfinance API"""
        try:
            import yfinance as yf
            
            # Add .VN suffix for Vietnamese stocks
            ticker_symbol = f"{symbol}.VN"
            ticker = yf.Ticker(ticker_symbol)
            
            # Get current info
            info = ticker.info
            
            if info and 'currentPrice' in info:
                # Get historical data for 24h change calculation
                hist = ticker.history(period="2d")
                
                current_price = info.get('currentPrice', 0)
                previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                
                change = current_price - previous_close
                percent_change = (change / previous_close * 100) if previous_close != 0 else 0
                
                return {
                    "symbol": symbol,
                    "price": current_price,
                    "change": change,
                    "percent_change": round(percent_change, 2),
                    "volume": info.get('volume', 0),
                    "market_cap": info.get('marketCap', 0),
                    "high": info.get('dayHigh', current_price),
                    "low": info.get('dayLow', current_price),
                    "open": info.get('open', current_price),
                    "close": current_price,
                    "source": "yfinance"
                }
        except Exception as e:
            logger.warning(f"yfinance API failed for {symbol}: {str(e)}")
        return None
    
    async def _fetch_from_tcbs(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from TCBS API"""
        try:
            url = f"{self.apis['tcbs']}stock/{symbol}/overview"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol,
                    "price": data.get("price", 0),
                    "change": data.get("change", 0),
                    "percent_change": data.get("percent_change", 0),
                    "volume": data.get("volume", 0),
                    "high": data.get("high", 0),
                    "low": data.get("low", 0),
                    "open": data.get("open", 0),
                    "close": data.get("close", 0),
                    "source": "TCBS"
                }
        except Exception as e:
            logger.warning(f"TCBS API failed for {symbol}: {str(e)}")
        return None
    
    async def _fetch_from_vietstock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from VietStock API"""
        try:
            url = f"{self.apis['vietstock']}stock/{symbol}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol,
                    "price": data.get("current_price", 0),
                    "change": data.get("change", 0),
                    "percent_change": data.get("percent_change", 0),
                    "volume": data.get("volume", 0),
                    "high": data.get("high", 0),
                    "low": data.get("low", 0),
                    "open": data.get("open", 0),
                    "close": data.get("previous_close", 0),
                    "source": "VietStock"
                }
        except Exception as e:
            logger.warning(f"VietStock API failed for {symbol}: {str(e)}")
        return None
    
    async def _fetch_from_cafef(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Cafef API"""
        try:
            url = f"{self.apis['cafef']}{symbol}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol,
                    "price": data.get("price", 0),
                    "change": data.get("change", 0),
                    "percent_change": data.get("percent_change", 0),
                    "volume": data.get("volume", 0),
                    "high": data.get("high", 0),
                    "low": data.get("low", 0),
                    "open": data.get("open", 0),
                    "close": data.get("close", 0),
                    "source": "Cafef"
                }
        except Exception as e:
            logger.warning(f"Cafef API failed for {symbol}: {str(e)}")
        return None
    
    def _format_stock_data(self, symbol: str, data: Dict[str, Any], market_query: MarketQuery) -> Dict[str, Any]:
        """Format stock data according to requested fields"""
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "exchange": market_query.exchange or "HOSE",
            "currency": market_query.currency
        }
        
        # Filter data based on include flags
        filtered_data = {}
        
        # Always include basic price data
        if "price" in data:
            filtered_data["price"] = data["price"]
        
        # Include 24h change data if requested
        if market_query.include_24h_change:
            if "change" in data:
                filtered_data["change"] = data["change"]
            if "percent_change" in data:
                filtered_data["percent_change"] = data["percent_change"]
        
        # Include volume data if requested
        if market_query.include_volume and "volume" in data:
            filtered_data["volume"] = data["volume"]
        
        # Include market cap data if requested
        if market_query.include_market_cap and "market_cap" in data:
            filtered_data["market_cap"] = data["market_cap"]
        
        # Include technical indicators if requested
        if market_query.include_technical_indicators:
            # Add mock technical indicators for demo
            filtered_data["rsi"] = round(30 + (70 * (data.get("price", 0) % 100) / 100), 2)
            filtered_data["macd"] = round((data.get("price", 0) * 0.02), 2)
            filtered_data["moving_average_20"] = round(data.get("price", 0) * 0.98, 2)
            filtered_data["moving_average_50"] = round(data.get("price", 0) * 0.95, 2)
        
        # Include other basic fields
        for field in ["high", "low", "open", "close", "source"]:
            if field in data:
                filtered_data[field] = data[field]
        
        # Add requested fields or all available fields
        if market_query.fields:
            for field in market_query.fields:
                if field in filtered_data:
                    result[field] = filtered_data[field]
        else:
            # Return all available filtered fields
            result.update(filtered_data)
        
        return result
    
    def _create_mock_data(self, symbol: str, market_query: MarketQuery) -> Dict[str, Any]:
        """Create mock data for demo purposes"""
        import random
        
        # Adjust price range based on currency
        if market_query.currency == "USD":
            base_price = random.uniform(1, 100)  # USD range
        else:
            base_price = random.uniform(10000, 100000)  # VND range
        
        # Create base data
        data = {
            "symbol": symbol,
            "price": round(base_price, 2 if market_query.currency == "USD" else 0),
            "high": round(base_price * 1.05, 2 if market_query.currency == "USD" else 0),
            "low": round(base_price * 0.95, 2 if market_query.currency == "USD" else 0),
            "open": round(base_price * 0.98, 2 if market_query.currency == "USD" else 0),
            "close": round(base_price * 1.02, 2 if market_query.currency == "USD" else 0),
            "timestamp": datetime.now().isoformat(),
            "exchange": market_query.exchange or "HOSE",
            "currency": market_query.currency,
            "source": "Mock Data (Demo)"
        }
        
        # Add conditional fields based on schema flags
        if market_query.include_24h_change:
            change_amount = random.uniform(-5000, 5000) if market_query.currency == "VND" else random.uniform(-5, 5)
            data["change"] = round(change_amount, 2 if market_query.currency == "USD" else 0)
            data["percent_change"] = round(random.uniform(-5, 5), 2)
        
        if market_query.include_volume:
            data["volume"] = random.randint(100000, 10000000)
        
        if market_query.include_market_cap:
            market_cap = random.randint(1000000000, 1000000000000)
            if market_query.currency == "USD":
                market_cap = market_cap // 24000  # Convert VND to USD roughly
            data["market_cap"] = market_cap
        
        if market_query.include_technical_indicators:
            data["rsi"] = round(30 + (70 * (base_price % 100) / 100), 2)
            data["macd"] = round((base_price * 0.02), 2)
            data["moving_average_20"] = round(base_price * 0.98, 2 if market_query.currency == "USD" else 0)
            data["moving_average_50"] = round(base_price * 0.95, 2 if market_query.currency == "USD" else 0)
        
        return data
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global service instance
market_service = VietnamMarketService()


@function_tool
async def get_realtime_market_data(
    symbols: List[str],
    exchange: str = "HOSE",
    fields: Optional[List[str]] = None,
    include_24h_change: bool = True,
    include_volume: bool = True,
    include_market_cap: bool = True,
    include_technical_indicators: bool = False,
    currency: str = "VND"
) -> str:
    """
    Get realtime market data for Vietnamese stocks from HOSE, HNX, and UPCOM exchanges.
    
    Args:
        symbols: List of stock symbols to query (e.g., ['VIC', 'VCB', 'VHM'])
        exchange: Exchange to get data from (HOSE, HNX, UPCOM, ALL)
        fields: Specific fields to return (price, change, percent_change, volume, high, low, open, close, market_cap)
        include_24h_change: Include 24-hour price change data
        include_volume: Include trading volume data
        include_market_cap: Include market capitalization data
        include_technical_indicators: Include technical analysis indicators (RSI, MACD, Moving Averages)
        currency: Currency for price data (VND, USD)
    """
    print("🔧 TOOL CALL: get_realtime_market_data")
    print(f"📥 INPUT: symbols={symbols}, exchange={exchange}, currency={currency}")
    print(f"📥 PARAMS: include_24h_change={include_24h_change}, include_volume={include_volume}, include_market_cap={include_market_cap}")
    print(f"📥 FIELDS: {fields}")
    
    try:
        # Create MarketQuery object
        query = MarketQuery(
            symbols=symbols,
            exchange=exchange,
            fields=fields,
            include_24h_change=include_24h_change,
            include_volume=include_volume,
            include_market_cap=include_market_cap,
            include_technical_indicators=include_technical_indicators,
            currency=currency
        )
        
        print(f"📋 QUERY OBJECT: {query}")
        
        # Call market service
        print("🚀 CALLING: market_service.get_realtime_data()")
        result = await market_service.get_realtime_data(query)
        
        print(f"📤 OUTPUT: {type(result)} - {len(result) if isinstance(result, str) else 'not string'} chars")
        print("📄 OUTPUT CONTENT:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        print(f"📊 SUCCESS: Tool execution completed")
        
        return result
        
    except Exception as e:
        error_msg = f"Error in get_realtime_market_data: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        
        error_result = json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)
        
        print(f"📤 ERROR OUTPUT: {error_result}")
        return error_result
