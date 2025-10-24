"""
Simple tests to check if tools can fetch market data
"""
import asyncio
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


async def test_crypto_market():
    """Test crypto market data fetching"""
    print("🔍 Testing Crypto Market...")
    
    try:
        from src.tools.crypto_market import CryptoQuery, CryptoMarketService
        
        # Create query
        query = CryptoQuery(
            symbols=["BTC", "ETH"],
            vs_currency="usd",
            include_24h_change=True,
            include_volume=True,
            include_market_cap=True
        )
        
        # Create service
        service = CryptoMarketService()
        
        # Test data fetching
        result = await service.get_realtime_data(query)
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print("✅ Crypto Market: SUCCESS")
            print(f"   - Symbols requested: {len(query.symbols)}")
            print(f"   - Data returned: {len(result_data.get('data', []))}")
            print(f"   - Sample data: {result_data.get('data', [{}])[0] if result_data.get('data') else 'None'}")
        else:
            print("❌ Crypto Market: FAILED")
            print(f"   - Error: {result_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Crypto Market: ERROR - {str(e)}")
    
    finally:
        try:
            await service.close()
        except:
            pass


async def test_stock_market():
    """Test stock market data fetching"""
    print("\n🔍 Testing Stock Market...")
    
    try:
        from src.tools.stock_market import MarketQuery, VietnamMarketService
        
        # Create query
        query = MarketQuery(
            symbols=["VIC", "VCB"],
            exchange="HOSE",
            currency="VND",
            include_24h_change=True,
            include_volume=True,
            include_market_cap=True
        )
        
        # Create service
        service = VietnamMarketService()
        
        # Test data fetching
        result = await service.get_realtime_data(query)
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print("✅ Stock Market: SUCCESS")
            print(f"   - Symbols requested: {len(query.symbols)}")
            print(f"   - Data returned: {len(result_data.get('data', []))}")
            print(f"   - Sample data: {result_data.get('data', [{}])[0] if result_data.get('data') else 'None'}")
        else:
            print("❌ Stock Market: FAILED")
            print(f"   - Error: {result_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Stock Market: ERROR - {str(e)}")
    
    finally:
        try:
            await service.close()
        except:
            pass


async def test_retrieval_tool():
    """Test retrieval tool"""
    print("\n🔍 Testing Retrieval Tool...")
    
    try:
        from src.tools.retrieval_tool import RetrievalQuery, RetrievalService
        
        # Create query
        query = RetrievalQuery(
            query="thông tin về cổ phiếu VIC",
            data_sources=["documents", "databases"],
            max_results=5,
            include_metadata=True,
            include_snippets=True,
            language="vi"
        )
        
        # Create service
        service = RetrievalService()
        
        # Test data fetching (this will likely fail since no API is running)
        result = await service.retrieve_data(query)
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print("✅ Retrieval Tool: SUCCESS")
            print(f"   - Query: {query.query}")
            print(f"   - Results: {len(result_data.get('results', []))}")
        else:
            print("⚠️  Retrieval Tool: EXPECTED FAILURE (No API running)")
            print(f"   - Error: {result_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Retrieval Tool: ERROR - {str(e)}")
    
    finally:
        try:
            await service.close()
        except:
            pass


def test_schemas():
    """Test schema validation"""
    print("\n🔍 Testing Schemas...")
    
    try:
        from src.tools.crypto_market import CryptoQuery
        from src.tools.stock_market import MarketQuery
        from src.tools.retrieval_tool import RetrievalQuery
        
        # Test CryptoQuery
        crypto_query = CryptoQuery(symbols=["BTC", "ETH"])
        print("✅ CryptoQuery schema: OK")
        
        # Test MarketQuery
        market_query = MarketQuery(symbols=["VIC", "VCB"])
        print("✅ MarketQuery schema: OK")
        
        # Test RetrievalQuery
        retrieval_query = RetrievalQuery(query="test query")
        print("✅ RetrievalQuery schema: OK")
        
    except Exception as e:
        print(f"❌ Schema validation: ERROR - {str(e)}")


async def main():
    """Run all tests"""
    print("🚀 Starting Simple Market Data Tests...\n")
    
    # Test schemas first
    test_schemas()
    
    # Test market data fetching
    await test_crypto_market()
    await test_stock_market()
    await test_retrieval_tool()
    
    print("\n✨ Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
