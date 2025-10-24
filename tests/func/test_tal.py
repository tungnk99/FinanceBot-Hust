#!/usr/bin/env python3
"""
Test TAL stock with yfinance
"""
import asyncio
import json
import sys
import os

# Add src to path
sys.path.append('src')

async def test_tal_stock():
    """Test TAL stock data"""
    print("🔍 Testing TAL Stock...")
    
    from src.tools.stock_market import MarketQuery, VietnamMarketService
    
    # Test with TAL symbol
    query = MarketQuery(
        symbols=['TAL'],
        exchange='HOSE',
        currency='VND',
        include_24h_change=True,
        include_volume=True,
        include_market_cap=True,
        include_technical_indicators=True
    )
    
    service = VietnamMarketService()
    
    result = await service.get_realtime_data(query)
    data = json.loads(result)
    
    print(f"Success: {data.get('success')}")
    print(f"Data count: {len(data.get('data', []))}")
    
    if data.get('data'):
        item = data['data'][0]
        print(f"\n=== TAL DATA ===")
        print(f"Symbol: {item.get('symbol')}")
        print(f"Price: {item.get('price')} VND")
        print(f"Source: {item.get('source')}")
        print(f"Change: {item.get('change')} VND")
        print(f"Percent Change: {item.get('percent_change')}%")
        print(f"Volume: {item.get('volume')}")
        print(f"Market Cap: {item.get('market_cap')}")
        print(f"High: {item.get('high')}")
        print(f"Low: {item.get('low')}")
        print(f"Open: {item.get('open')}")
        print(f"Close: {item.get('close')}")
        
        # Check technical indicators
        if 'rsi' in item:
            print(f"RSI: {item.get('rsi')}")
            print(f"MACD: {item.get('macd')}")
            print(f"MA20: {item.get('moving_average_20')}")
            print(f"MA50: {item.get('moving_average_50')}")
        
        # Check if it's real data
        if item.get('source') == 'yfinance':
            print("✅ REAL DATA from yfinance API")
        elif 'Mock' in str(item.get('source', '')):
            print("⚠️  MOCK DATA")
        else:
            print(f"❓ UNKNOWN SOURCE: {item.get('source')}")
    else:
        print("❌ No data returned")
    
    await service.close()

async def test_tal_direct_yfinance():
    """Test TAL directly with yfinance"""
    print("\n🔍 Testing TAL directly with yfinance...")
    
    try:
        import yfinance as yf
        
        # Test TAL.VN
        ticker = yf.Ticker("TAL.VN")
        info = ticker.info
        
        print(f"TAL.VN Info available: {bool(info)}")
        if info:
            print(f"Current Price: {info.get('currentPrice', 'N/A')}")
            print(f"Currency: {info.get('currency', 'N/A')}")
            print(f"Market Cap: {info.get('marketCap', 'N/A')}")
            print(f"Volume: {info.get('volume', 'N/A')}")
            print(f"Day High: {info.get('dayHigh', 'N/A')}")
            print(f"Day Low: {info.get('dayLow', 'N/A')}")
            print(f"Open: {info.get('open', 'N/A')}")
            
            # Get historical data
            hist = ticker.history(period="5d")
            print(f"Historical data available: {len(hist)} days")
            if len(hist) > 0:
                print(f"Latest close: {hist['Close'].iloc[-1]}")
                if len(hist) > 1:
                    print(f"Previous close: {hist['Close'].iloc[-2]}")
        else:
            print("❌ No data available for TAL.VN")
            
    except Exception as e:
        print(f"❌ Error testing TAL.VN: {str(e)}")

async def test_other_vietnamese_stocks():
    """Test other Vietnamese stocks"""
    print("\n🔍 Testing other Vietnamese stocks...")
    
    stocks = ['VCB', 'VHM', 'HPG', 'MSN', 'VRE', 'GAS', 'VIC', 'CTG', 'BID', 'TCB']
    
    try:
        import yfinance as yf
        
        for stock in stocks:
            try:
                ticker = yf.Ticker(f"{stock}.VN")
                info = ticker.info
                
                if info and 'currentPrice' in info:
                    print(f"✅ {stock}: {info.get('currentPrice')} VND")
                else:
                    print(f"❌ {stock}: No data")
                    
            except Exception as e:
                print(f"❌ {stock}: Error - {str(e)}")
                
    except Exception as e:
        print(f"❌ Error testing stocks: {str(e)}")

async def main():
    """Run TAL tests"""
    print("🚀 Testing TAL Stock...\n")
    
    await test_tal_stock()
    await test_tal_direct_yfinance()
    await test_other_vietnamese_stocks()
    
    print("\n✨ TAL testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
