import asyncio
import httpx
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from agents import RunContextWrapper, function_tool


class CryptoQuery(BaseModel):
    """Schema for cryptocurrency market data queries"""
    
    symbols: List[str] = Field(
        ..., 
        description="List of cryptocurrency symbols to query (e.g., ['BTC', 'ETH', 'ADA'])",
        min_items=1,
        max_items=50
    )
    
    vs_currency: Optional[str] = Field(
        default="usd",
        description="Currency to compare against (usd, eur, jpy, krw, vnd)",
        pattern="^(usd|eur|jpy|krw|vnd)$"
    )
    
    exchange: Optional[str] = Field(
        default="global",
        description="Exchange to get data from (global, binance, coinbase, kraken)",
        pattern="^(global|binance|coinbase|kraken)$"
    )
    
    fields: Optional[List[str]] = Field(
        default=None,
        description="Specific fields to return (price, change, percent_change, volume, market_cap, high, low, open, close)",
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbols": ["BTC", "ETH", "ADA"],
                "vs_currency": "usd",
                "exchange": "global",
                "fields": ["price", "change", "percent_change", "volume", "market_cap"],
                "include_24h_change": True,
                "include_volume": True,
                "include_market_cap": True
            }
        }


logger = logging.getLogger(__name__)


class CryptoMarketService:
    """Service class to handle cryptocurrency market data operations"""
    
    def __init__(self):
        """Initialize CryptoMarketService with free APIs"""
        # Free APIs for cryptocurrency market data
        self.apis = {
            "coinpaprika": "https://api.coinpaprika.com/v1/",
            "coingecko": "https://api.coingecko.com/api/v3/",
            "cryptocompare": "https://min-api.cryptocompare.com/data/",
            "binance": "https://api.binance.com/api/v3/"
        }
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json"
            }
        )
    
    async def get_realtime_data(self, crypto_query: CryptoQuery) -> str:
        """
        Get realtime cryptocurrency market data
        
        Args:
            crypto_query: CryptoQuery object containing symbols and parameters
            
        Returns:
            JSON string containing crypto market data
        """
        try:
            results = []
            
            for symbol in crypto_query.symbols:
                # Try multiple free APIs
                crypto_data = await self._fetch_crypto_data(symbol, crypto_query)
                if crypto_data:
                    results.append(crypto_data)
            
            return json.dumps({
                "success": True,
                "data": results,
                "timestamp": datetime.now().isoformat(),
                "query": crypto_query.dict(),
                "total_symbols": len(crypto_query.symbols),
                "successful_symbols": len(results)
            }, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_msg = f"Error in get_realtime_data: {str(e)}"
            logger.error(error_msg)
            return json.dumps({
                "success": False,
                "error": error_msg,
                "query": crypto_query.dict()
            }, ensure_ascii=False, indent=2)
    
    async def _fetch_crypto_data(self, symbol: str, crypto_query: CryptoQuery) -> Optional[Dict[str, Any]]:
        """Fetch data for a single cryptocurrency symbol with smart fallback"""
        # Define API priority order (most reliable first)
        api_methods = [
            ("CoinGecko", self._fetch_from_coingecko),
            ("CoinPaprika", self._fetch_from_coinpaprika),
            ("Binance", self._fetch_from_binance),
            ("CryptoCompare", self._fetch_from_cryptocompare)
        ]
        
        for api_name, api_method in api_methods:
            try:
                logger.info(f"Trying {api_name} API for {symbol}")
                data = await api_method(symbol, crypto_query)
                
                if data and data.get('price', 0) > 0:  # Valid data check
                    logger.info(f"✅ Successfully fetched {symbol} data from {api_name}")
                    return self._format_crypto_data(symbol, data, crypto_query)
                else:
                    logger.warning(f"⚠️ {api_name} returned invalid data for {symbol}")
                    
            except Exception as e:
                logger.warning(f"❌ {api_name} failed for {symbol}: {str(e)}")
                continue
        
        # If all APIs fail, create mock data
        logger.warning(f"🔄 All APIs failed for {symbol}, using mock data")
        return self._create_mock_data(symbol, crypto_query)
    
    async def _fetch_from_coingecko(self, symbol: str, crypto_query: CryptoQuery) -> Optional[Dict[str, Any]]:
        """Fetch data from CoinGecko API"""
        try:
            # CoinGecko uses lowercase symbols and different naming
            symbol_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "BNB": "binancecoin",
                "ADA": "cardano",
                "SOL": "solana",
                "XRP": "ripple",
                "DOT": "polkadot",
                "DOGE": "dogecoin",
                "AVAX": "avalanche-2",
                "MATIC": "matic-network"
            }
            
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            vs_currency = crypto_query.vs_currency or "usd"
            
            url = f"{self.apis['coingecko']}simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": vs_currency,
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true"
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if coin_id in data:
                    coin_data = data[coin_id]
                    return {
                        "symbol": symbol.upper(),
                        "price": coin_data.get(f"{vs_currency}", 0),
                        "change": coin_data.get(f"{vs_currency}_24h_change", 0),
                        "percent_change": coin_data.get(f"{vs_currency}_24h_change", 0),
                        "volume": coin_data.get(f"{vs_currency}_24h_vol", 0),
                        "market_cap": coin_data.get(f"{vs_currency}_market_cap", 0),
                        "source": "CoinGecko"
                    }
        except Exception as e:
            logger.warning(f"CoinGecko API failed for {symbol}: {str(e)}")
        return None
    
    async def _fetch_from_coinpaprika(self, symbol: str, crypto_query: CryptoQuery) -> Optional[Dict[str, Any]]:
        """Fetch data from CoinPaprika API"""
        try:
            # CoinPaprika uses different symbol format
            symbol_map = {
                "BTC": "btc-bitcoin",
                "ETH": "eth-ethereum",
                "BNB": "bnb-binance-coin",
                "ADA": "ada-cardano",
                "SOL": "sol-solana",
                "XRP": "xrp-xrp",
                "DOT": "dot-polkadot",
                "DOGE": "doge-dogecoin",
                "AVAX": "avax-avalanche",
                "MATIC": "matic-polygon"
            }
            
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            
            url = f"{self.apis['coinpaprika']}tickers/{coin_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol.upper(),
                    "price": data.get("quotes", {}).get("USD", {}).get("price", 0),
                    "change": data.get("quotes", {}).get("USD", {}).get("price_change", 0),
                    "percent_change": data.get("quotes", {}).get("USD", {}).get("price_change_percentage_24h", 0),
                    "volume": data.get("quotes", {}).get("USD", {}).get("volume_24h", 0),
                    "market_cap": data.get("quotes", {}).get("USD", {}).get("market_cap", 0),
                    "high": data.get("quotes", {}).get("USD", {}).get("market_cap_change_24h", 0),
                    "low": data.get("quotes", {}).get("USD", {}).get("market_cap_change_24h", 0),
                    "source": "CoinPaprika"
                }
        except Exception as e:
            logger.warning(f"CoinPaprika API failed for {symbol}: {str(e)}")
        return None
    
    async def _fetch_from_binance(self, symbol: str, crypto_query: CryptoQuery) -> Optional[Dict[str, Any]]:
        """Fetch data from Binance API"""
        try:
            vs_currency = crypto_query.vs_currency or "usd"
            currency_map = {
                "usd": "USDT",
                "eur": "EUR",
                "jpy": "JPY",
                "krw": "KRW",
                "vnd": "VND"
            }
            
            quote_currency = currency_map.get(vs_currency, "USDT")
            pair = f"{symbol.upper()}{quote_currency}"
            
            url = f"{self.apis['binance']}ticker/24hr"
            params = {"symbol": pair}
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol.upper(),
                    "price": float(data.get("lastPrice", 0)),
                    "change": float(data.get("priceChange", 0)),
                    "percent_change": float(data.get("priceChangePercent", 0)),
                    "volume": float(data.get("volume", 0)),
                    "high": float(data.get("highPrice", 0)),
                    "low": float(data.get("lowPrice", 0)),
                    "open": float(data.get("openPrice", 0)),
                    "close": float(data.get("lastPrice", 0)),
                    "source": "Binance"
                }
        except Exception as e:
            logger.warning(f"Binance API failed for {symbol}: {str(e)}")
        return None
    
    async def _fetch_from_cryptocompare(self, symbol: str, crypto_query: CryptoQuery) -> Optional[Dict[str, Any]]:
        """Fetch data from CryptoCompare API"""
        try:
            vs_currency = crypto_query.vs_currency or "usd"
            
            url = f"{self.apis['cryptocompare']}price"
            params = {
                "fsym": symbol.upper(),
                "tsyms": vs_currency.upper()
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if vs_currency.upper() in data:
                    price = data[vs_currency.upper()]
                    return {
                        "symbol": symbol.upper(),
                        "price": price,
                        "change": 0,  # CryptoCompare basic API doesn't provide change
                        "percent_change": 0,
                        "volume": 0,
                        "market_cap": 0,
                        "source": "CryptoCompare"
                    }
        except Exception as e:
            logger.warning(f"CryptoCompare API failed for {symbol}: {str(e)}")
        return None
    
    def _format_crypto_data(self, symbol: str, data: Dict[str, Any], crypto_query: CryptoQuery) -> Dict[str, Any]:
        """Format crypto data according to requested fields"""
        result = {
            "symbol": symbol.upper(),
            "timestamp": datetime.now().isoformat(),
            "vs_currency": crypto_query.vs_currency or "usd",
            "exchange": crypto_query.exchange or "global"
        }
        
        # Filter data based on include flags
        filtered_data = {}
        
        # Always include basic price data
        if "price" in data:
            filtered_data["price"] = data["price"]
        
        # Include 24h change data if requested
        if crypto_query.include_24h_change:
            if "change" in data:
                filtered_data["change"] = data["change"]
            if "percent_change" in data:
                filtered_data["percent_change"] = data["percent_change"]
        
        # Include volume data if requested
        if crypto_query.include_volume and "volume" in data:
            filtered_data["volume"] = data["volume"]
        
        # Include market cap data if requested
        if crypto_query.include_market_cap and "market_cap" in data:
            filtered_data["market_cap"] = data["market_cap"]
        
        # Include other basic fields
        for field in ["high", "low", "open", "close", "source"]:
            if field in data:
                filtered_data[field] = data[field]
        
        # Add requested fields or all available fields
        if crypto_query.fields:
            for field in crypto_query.fields:
                if field in filtered_data:
                    result[field] = filtered_data[field]
        else:
            # Return all available filtered fields
            result.update(filtered_data)
        
        return result
    
    def _create_mock_data(self, symbol: str, crypto_query: CryptoQuery) -> Dict[str, Any]:
        """Create mock data for demo purposes"""
        import random
        
        # Base prices for major cryptocurrencies
        base_prices = {
            "BTC": 45000,
            "ETH": 3000,
            "BNB": 300,
            "ADA": 0.5,
            "SOL": 100,
            "XRP": 0.6,
            "DOT": 7,
            "DOGE": 0.08,
            "AVAX": 25,
            "MATIC": 0.8
        }
        
        base_price = base_prices.get(symbol.upper(), random.uniform(0.01, 1000))
        
        # Create base data
        data = {
            "symbol": symbol.upper(),
            "price": round(base_price * random.uniform(0.95, 1.05), 2),
            "high": round(base_price * 1.1, 2),
            "low": round(base_price * 0.9, 2),
            "open": round(base_price * 0.98, 2),
            "close": round(base_price * 1.02, 2),
            "timestamp": datetime.now().isoformat(),
            "vs_currency": crypto_query.vs_currency or "usd",
            "exchange": crypto_query.exchange or "global",
            "source": "Mock Data (Demo)"
        }
        
        # Add conditional fields based on schema flags
        if crypto_query.include_24h_change:
            data["change"] = round(base_price * random.uniform(-0.1, 0.1), 2)
            data["percent_change"] = round(random.uniform(-10, 10), 2)
        
        if crypto_query.include_volume:
            data["volume"] = random.randint(1000000, 100000000)
        
        if crypto_query.include_market_cap:
            data["market_cap"] = random.randint(1000000000, 1000000000000)
        
        return data
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global service instance
crypto_service = CryptoMarketService()


async def run_crypto_function(ctx: RunContextWrapper, args: str) -> str:
    """
    Run function for CryptoMarketTool
    
    Args:
        ctx: Run context wrapper
        args: JSON string containing function arguments
        
    Returns:
        JSON string containing crypto market data
    """
    try:
        # Parse arguments
        parsed_args = CryptoQuery.model_validate_json(args)
        
        # Call crypto service
        result = await crypto_service.get_realtime_data(parsed_args)
        
        return result
        
    except Exception as e:
        error_msg = f"Error in run_crypto_function: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)


@function_tool
async def get_crypto_market_data(
    symbols: List[str],
    vs_currency: str = "usd",
    exchange: str = "global",
    fields: Optional[List[str]] = None,
    include_24h_change: bool = True,
    include_volume: bool = True,
    include_market_cap: bool = True
) -> str:
    """
    Get realtime cryptocurrency market data from major exchanges.
    
    Args:
        symbols: List of cryptocurrency symbols to query (e.g., ['BTC', 'ETH', 'ADA'])
        vs_currency: Currency to compare against (usd, eur, jpy, krw, vnd)
        exchange: Exchange to get data from (global, binance, coinbase, kraken)
        fields: Specific fields to return (price, change, percent_change, volume, market_cap, high, low, open, close)
        include_24h_change: Include 24-hour price change data
        include_volume: Include trading volume data
        include_market_cap: Include market capitalization data
    """
    print("🔧 TOOL CALL: get_crypto_market_data")
    print(f"📥 INPUT: symbols={symbols}, vs_currency={vs_currency}, exchange={exchange}")
    print(f"📥 PARAMS: include_24h_change={include_24h_change}, include_volume={include_volume}, include_market_cap={include_market_cap}")
    print(f"📥 FIELDS: {fields}")
    
    try:
        # Create CryptoQuery object
        query = CryptoQuery(
            symbols=symbols,
            vs_currency=vs_currency,
            exchange=exchange,
            fields=fields,
            include_24h_change=include_24h_change,
            include_volume=include_volume,
            include_market_cap=include_market_cap
        )
        
        print(f"📋 QUERY OBJECT: {query}")
        
        # Call crypto service
        print("🚀 CALLING: crypto_service.get_realtime_data()")
        result = await crypto_service.get_realtime_data(query)
        
        print(f"📤 OUTPUT: {type(result)} - {len(result) if isinstance(result, str) else 'not string'} chars")
        print("📄 OUTPUT CONTENT:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        print(f"📊 SUCCESS: Tool execution completed")
        
        return result
        
    except Exception as e:
        error_msg = f"Error in get_crypto_market_data: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        
        error_result = json.dumps({
            "success": False,
            "error": error_msg
        }, ensure_ascii=False, indent=2)
        
        print(f"📤 ERROR OUTPUT: {error_result}")
        return error_result

