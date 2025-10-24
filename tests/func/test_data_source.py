#!/usr/bin/env python3
"""
Test to check if data is real or mock
"""
import asyncio
import json
import sys
import os

# Add src to path
sys.path.append('src')

async def test_crypto_data_source():
    """Test crypto market data source"""
    print("🔍 Testing Crypto Market Data Source...")
    
    from src.tools.crypto_market import CryptoQuery, CryptoMarketService
    
    query = CryptoQuery(symbols=['BTC'])
    service = CryptoMarketService()
    
    result = await service.get_realtime_data(query)
    data = json.loads(result)
    
    print(f"Success: {data.get('success')}")
    print(f"Data count: {len(data.get('data', []))}")
    
    if data.get('data'):
        item = data['data'][0]
        print(f"\n=== BTC DATA ===")
        print(f"Symbol: {item.get('symbol')}")
        print(f"Price: ${item.get('price')}")
        print(f"Source: {item.get('source')}")
        print(f"Change: {item.get('change')}%")
        print(f"Volume: {item.get('volume')}")
        print(f"Market Cap: {item.get('market_cap')}")
        
        # Check if it's real data
        if item.get('source') == 'CoinGecko':
            print("✅ REAL DATA from CoinGecko API")
        elif item.get('source') == 'CoinPaprika':
            print("✅ REAL DATA from CoinPaprika API")
        elif item.get('source') == 'Binance':
            print("✅ REAL DATA from Binance API")
        elif 'Mock' in str(item.get('source', '')):
            print("⚠️  MOCK DATA")
        else:
            print(f"❓ UNKNOWN SOURCE: {item.get('source')}")
    
    await service.close()

async def test_stock_data_source():
    """Test stock market data source"""
    print("\n🔍 Testing Stock Market Data Source...")
    
    from src.tools.stock_market import MarketQuery, VietnamMarketService
    
    query = MarketQuery(symbols=['VIC'])
    service = VietnamMarketService()
    
    result = await service.get_realtime_data(query)
    data = json.loads(result)
    
    print(f"Success: {data.get('success')}")
    print(f"Data count: {len(data.get('data', []))}")
    
    if data.get('data'):
        item = data['data'][0]
        print(f"\n=== VIC DATA ===")
        print(f"Symbol: {item.get('symbol')}")
        print(f"Price: {item.get('price')} VND")
        print(f"Source: {item.get('source')}")
        print(f"Change: {item.get('change')} VND")
        print(f"Volume: {item.get('volume')}")
        print(f"Market Cap: {item.get('market_cap')}")
        
        # Check if it's real data
        if item.get('source') == 'yfinance':
            print("✅ REAL DATA from yfinance API")
        elif item.get('source') == 'TCBS':
            print("✅ REAL DATA from TCBS API")
        elif item.get('source') == 'VietStock':
            print("✅ REAL DATA from VietStock API")
        elif 'Mock' in str(item.get('source', '')):
            print("⚠️  MOCK DATA")
        else:
            print(f"❓ UNKNOWN SOURCE: {item.get('source')}")
    
    await service.close()

async def main():
    """Run data source tests"""
    print("🚀 Testing Data Sources...\n")
    
    await test_crypto_data_source()
    await test_stock_data_source()
    
    print("\n✨ Data source testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
