#!/usr/bin/env python3
"""
Test stock market APIs availability
"""
import asyncio
import httpx
import json
import sys
import os

# Add src to path
sys.path.append('src')

async def test_tcbs_api():
    """Test TCBS API"""
    print("🔍 Testing TCBS API...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test with VIC symbol
            url = "https://apipubaws.tcbs.com.vn/tcanalysis/v1/stock/VIC/overview"
            response = await client.get(url)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ TCBS API: SUCCESS")
                print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print(f"Sample data: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ TCBS API: FAILED - {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ TCBS API: ERROR - {str(e)}")
        return False

async def test_vietstock_api():
    """Test VietStock API"""
    print("\n🔍 Testing VietStock API...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test with VIC symbol
            url = "https://finance.vietstock.vn/data/stock/VIC"
            response = await client.get(url)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ VietStock API: SUCCESS")
                print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print(f"Sample data: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ VietStock API: FAILED - {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ VietStock API: ERROR - {str(e)}")
        return False

async def test_cafef_api():
    """Test Cafef API"""
    print("\n🔍 Testing Cafef API...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test with VIC symbol
            url = "https://s.cafef.vn/Ajax/PageNew/DataHistory/VIC"
            response = await client.get(url)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Cafef API: SUCCESS")
                print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print(f"Sample data: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ Cafef API: FAILED - {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ Cafef API: ERROR - {str(e)}")
        return False

async def test_alternative_apis():
    """Test alternative APIs"""
    print("\n🔍 Testing Alternative APIs...")
    
    # Test some alternative Vietnamese stock APIs
    apis = [
        {
            "name": "SSI API",
            "url": "https://iboard.ssi.com.vn/dchart/api/history?resolution=1&symbol=VIC&from=1640995200&to=1641081600"
        },
        {
            "name": "VNDirect API", 
            "url": "https://finfo-api.vndirect.com.vn/v4/stock_prices/VIC"
        },
        {
            "name": "FPT Securities API",
            "url": "https://api.fpts.com.vn/api/v1/stock/VIC/price"
        }
    ]
    
    results = []
    
    for api in apis:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(api["url"])
                print(f"{api['name']}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ {api['name']}: SUCCESS")
                    results.append(api['name'])
                else:
                    print(f"❌ {api['name']}: FAILED - {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {api['name']}: ERROR - {str(e)}")
    
    return results

async def test_yfinance_vietnamese():
    """Test yfinance for Vietnamese stocks"""
    print("\n🔍 Testing yfinance for Vietnamese stocks...")
    
    try:
        import yfinance as yf
        
        # Test VIC (Vingroup)
        ticker = yf.Ticker("VIC.VN")
        info = ticker.info
        
        if info and 'currentPrice' in info:
            print("✅ yfinance VIC: SUCCESS")
            print(f"Current Price: {info.get('currentPrice')}")
            print(f"Currency: {info.get('currency')}")
            print(f"Market Cap: {info.get('marketCap')}")
            return True
        else:
            print("❌ yfinance VIC: No data available")
            return False
            
    except Exception as e:
        print(f"❌ yfinance VIC: ERROR - {str(e)}")
        return False

async def main():
    """Run all API tests"""
    print("🚀 Testing Vietnamese Stock Market APIs...\n")
    
    results = {
        "TCBS": await test_tcbs_api(),
        "VietStock": await test_vietstock_api(), 
        "Cafef": await test_cafef_api(),
        "yfinance": await test_yfinance_vietnamese()
    }
    
    # Test alternative APIs
    alt_results = await test_alternative_apis()
    
    print("\n" + "="*50)
    print("📊 SUMMARY OF AVAILABLE APIs:")
    print("="*50)
    
    for api, available in results.items():
        status = "✅ AVAILABLE" if available else "❌ NOT AVAILABLE"
        print(f"{api:15}: {status}")
    
    if alt_results:
        print(f"\nAlternative APIs found: {', '.join(alt_results)}")
    else:
        print("\nNo alternative APIs found")
    
    print("\n💡 RECOMMENDATIONS:")
    if results["yfinance"]:
        print("- Use yfinance for Vietnamese stocks (VIC.VN format)")
    elif any(results.values()):
        available_apis = [api for api, avail in results.items() if avail]
        print(f"- Use available APIs: {', '.join(available_apis)}")
    else:
        print("- All APIs are down, consider using mock data or different data sources")
        print("- Try: Alpha Vantage, IEX Cloud, or other financial data providers")

if __name__ == "__main__":
    asyncio.run(main())
