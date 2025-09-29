"""
FinanceBot API Client Example
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional

class FinanceBotClient:
    """Client for FinanceBot FastAPI service"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def chat(self, message: str, query_type: Optional[str] = None, priority: str = "MEDIUM", session_id: Optional[str] = None) -> Dict[str, Any]:
        """Send chat message"""
        payload = {
            "message": message,
            "priority": priority,
            "session_id": session_id
        }
        
        if query_type:
            payload["query_type"] = query_type
        
        async with self.session.post(f"{self.base_url}/chat", json=payload) as response:
            return await response.json()
    
    async def analyze_stock(self, symbol: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze stock"""
        payload = {
            "symbol": symbol,
            "analysis_type": analysis_type
        }
        
        async with self.session.post(f"{self.base_url}/analyze/stock", json=payload) as response:
            return await response.json()
    
    async def quantitative_analysis(self, symbol: str, indicators: list = None) -> Dict[str, Any]:
        """Perform quantitative analysis"""
        if indicators is None:
            indicators = ["RSI", "MACD", "Moving Averages"]
        
        payload = {
            "symbol": symbol,
            "indicators": indicators
        }
        
        async with self.session.post(f"{self.base_url}/analyze/quantitative", json=payload) as response:
            return await response.json()
    
    async def generate_chart(self, symbol: str, chart_type: str = "price with moving averages") -> Dict[str, Any]:
        """Generate chart"""
        payload = {
            "symbol": symbol,
            "chart_type": chart_type
        }
        
        async with self.session.post(f"{self.base_url}/generate/chart", json=payload) as response:
            return await response.json()
    
    async def list_agents(self) -> Dict[str, Any]:
        """List available agents"""
        async with self.session.get(f"{self.base_url}/agents") as response:
            return await response.json()


async def demo():
    """Demo the FinanceBot API client"""
    print("🚀 FinanceBot API Client Demo")
    print("=" * 50)
    
    async with FinanceBotClient() as client:
        # Health check
        print("\n1. Health Check:")
        health = await client.health_check()
        print(f"Status: {health['status']}")
        print(f"Monitoring: {health['monitoring_enabled']}")
        
        # List agents
        print("\n2. Available Agents:")
        agents = await client.list_agents()
        print(f"Specialist Agents: {len(agents['specialist_agents'])}")
        print(f"Task Agents: {len(agents['task_agents'])}")
        
        # Chat example
        print("\n3. Chat Example:")
        chat_result = await client.chat(
            "Thị trường chứng khoán Việt Nam hôm nay như thế nào?",
            query_type="market_search"
        )
        
        if chat_result['success']:
            print(f"✅ Success!")
            print(f"Selected Agent: {chat_result['selected_agent']['agent_name']}")
            print(f"Response: {chat_result['response'][:200]}...")
        else:
            print(f"❌ Error: {chat_result['error']}")
        
        # Stock analysis
        print("\n4. Stock Analysis:")
        stock_result = await client.analyze_stock("VIC", "comprehensive")
        
        if stock_result['success']:
            print(f"✅ Success!")
            print(f"Selected Agent: {stock_result['selected_agent']['agent_name']}")
            print(f"Execution Time: {stock_result['execution_time']:.2f}s")
        else:
            print(f"❌ Error: {stock_result['error']}")
        
        # Quantitative analysis
        print("\n5. Quantitative Analysis:")
        quant_result = await client.quantitative_analysis("AAPL", ["RSI", "MACD", "Bollinger Bands"])
        
        if quant_result['success']:
            print(f"✅ Success!")
            print(f"Selected Agent: {quant_result['selected_agent']['agent_name']}")
        else:
            print(f"❌ Error: {quant_result['error']}")
        
        # Chart generation
        print("\n6. Chart Generation:")
        chart_result = await client.generate_chart("VIC", "price with Bollinger Bands")
        
        if chart_result['success']:
            print(f"✅ Success!")
            print(f"Selected Agent: {chart_result['selected_agent']['agent_name']}")
        else:
            print(f"❌ Error: {chart_result['error']}")
        
        print(f"\n✅ Demo completed!")


async def interactive_chat():
    """Interactive chat with FinanceBot"""
    print("🎯 FinanceBot Interactive Chat")
    print("Type 'quit' to exit")
    print("=" * 40)
    
    async with FinanceBotClient() as client:
        session_id = None
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 FinanceBot: Thinking...")
                result = await client.chat(user_input, session_id=session_id)
                
                if result['success']:
                    if not session_id:
                        session_id = result['session_id']
                    
                    print(f"✅ Success! Agent: {result['selected_agent']['agent_name']}")
                    print(f"📊 Response: {result['response']}")
                else:
                    print(f"❌ Error: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        asyncio.run(interactive_chat())
    else:
        asyncio.run(demo())
