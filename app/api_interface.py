"""
FinanceBot API Interface - Simplified interface for using FinanceBot
"""
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from app.main import FinanceBotApp
from src.agents.planner_agents.master_agent import MasterAgentRequest, QueryType, Priority

# Load environment variables
load_dotenv(".env", override=True)


class FinanceBotAPI:
    """Simplified API interface for FinanceBot"""
    
    def __init__(self):
        self.app = FinanceBotApp()
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the FinanceBot system"""
        if not self.is_initialized:
            success = await self.app.initialize()
            self.is_initialized = success
            return success
        return True
    
    async def ask(self, question: str, query_type: Optional[QueryType] = None, priority: Priority = Priority.MEDIUM) -> Dict[str, Any]:
        """
        Ask a question to FinanceBot
        
        Args:
            question: Your financial question
            query_type: Type of query (auto-detected if None)
            priority: Priority level (LOW, MEDIUM, HIGH, URGENT)
        
        Returns:
            Dict containing the response and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            result = await self.app.run_master_agent(question, query_type, priority)
            
            return {
                "success": True,
                "question": question,
                "answer": result.final_output,
                "query_type": query_type.value if query_type else "auto-detected",
                "priority": priority.value,
                "execution_time": getattr(result.final_output, 'execution_time', None),
                "selected_agent": getattr(result.final_output, 'selected_agent', None)
            }
            
        except Exception as e:
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "query_type": query_type.value if query_type else "auto-detected",
                "priority": priority.value
            }
    
    async def stock_research(self, symbol: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Perform stock research
        
        Args:
            symbol: Stock symbol (e.g., "VIC", "AAPL")
            analysis_type: Type of analysis ("comprehensive", "technical", "fundamental")
        
        Returns:
            Dict containing research results
        """
        query = f"Phân tích cổ phiếu {symbol} - {analysis_type} analysis về công ty và triển vọng đầu tư"
        return await self.ask(query, QueryType.STOCK_RESEARCH, Priority.HIGH)
    
    async def quantitative_analysis(self, symbol: str, indicators: str = "RSI, MACD, Moving Averages") -> Dict[str, Any]:
        """
        Perform quantitative analysis
        
        Args:
            symbol: Stock symbol (e.g., "VIC", "AAPL")
            indicators: Technical indicators to calculate
        
        Returns:
            Dict containing quantitative analysis results
        """
        query = f"Tính {indicators} cho cổ phiếu {symbol}"
        return await self.ask(query, QueryType.QUANTITATIVE_ANALYSIS, Priority.MEDIUM)
    
    async def generate_chart(self, symbol: str, chart_type: str = "price with moving averages") -> Dict[str, Any]:
        """
        Generate financial charts
        
        Args:
            symbol: Stock symbol (e.g., "VIC", "AAPL")
            chart_type: Type of chart to generate
        
        Returns:
            Dict containing chart generation results
        """
        query = f"Tạo biểu đồ {chart_type} cho cổ phiếu {symbol}"
        return await self.ask(query, QueryType.CHART_GENERATION, Priority.MEDIUM)
    
    async def risk_assessment(self, symbol: str, timeframe: str = "1 year") -> Dict[str, Any]:
        """
        Perform risk assessment
        
        Args:
            symbol: Stock symbol (e.g., "VIC", "AAPL")
            timeframe: Timeframe for risk analysis
        
        Returns:
            Dict containing risk assessment results
        """
        query = f"Đánh giá rủi ro cho cổ phiếu {symbol} trong {timeframe}"
        return await self.ask(query, QueryType.RISK_ASSESSMENT, Priority.MEDIUM)
    
    async def write_report(self, symbol: str, report_type: str = "investment analysis") -> Dict[str, Any]:
        """
        Generate investment report
        
        Args:
            symbol: Stock symbol (e.g., "VIC", "AAPL")
            report_type: Type of report to generate
        
        Returns:
            Dict containing report generation results
        """
        query = f"Viết báo cáo {report_type} cho cổ phiếu {symbol}"
        return await self.ask(query, QueryType.REPORT_WRITING, Priority.HIGH)
    
    async def search_market(self, query: str) -> Dict[str, Any]:
        """
        Search market information
        
        Args:
            query: Market search query
        
        Returns:
            Dict containing search results
        """
        return await self.ask(query, QueryType.MARKET_SEARCH, Priority.MEDIUM)
    
    async def shutdown(self):
        """Shutdown the FinanceBot system"""
        if self.is_initialized:
            await self.app.shutdown()
            self.is_initialized = False


# Convenience functions for direct usage
async def quick_ask(question: str) -> Dict[str, Any]:
    """Quick function to ask a question"""
    api = FinanceBotAPI()
    try:
        result = await api.ask(question)
        return result
    finally:
        await api.shutdown()


async def quick_stock_research(symbol: str) -> Dict[str, Any]:
    """Quick function to research a stock"""
    api = FinanceBotAPI()
    try:
        result = await api.stock_research(symbol)
        return result
    finally:
        await api.shutdown()


# Example usage
async def demo():
    """Demo function showing how to use the API"""
    api = FinanceBotAPI()
    
    try:
        print("🚀 FinanceBot API Demo")
        print("=" * 50)
        
        # Initialize
        await api.initialize()
        
        # Example 1: General question
        print("\n1. General Question:")
        result1 = await api.ask("Thị trường chứng khoán Việt Nam hôm nay như thế nào?")
        print(f"Success: {result1['success']}")
        if result1['success']:
            print(f"Answer: {result1['answer']}")
        
        # Example 2: Stock research
        print("\n2. Stock Research:")
        result2 = await api.stock_research("VIC")
        print(f"Success: {result2['success']}")
        if result2['success']:
            print(f"Selected Agent: {result2['selected_agent']}")
        
        # Example 3: Quantitative analysis
        print("\n3. Quantitative Analysis:")
        result3 = await api.quantitative_analysis("AAPL", "RSI, MACD, Bollinger Bands")
        print(f"Success: {result3['success']}")
        if result3['success']:
            print(f"Execution Time: {result3['execution_time']}")
        
    finally:
        await api.shutdown()


if __name__ == "__main__":
    asyncio.run(demo())
