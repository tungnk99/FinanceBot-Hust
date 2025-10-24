import asyncio
import pytest
from dotenv import load_dotenv
from agents import Runner
from src.agents.specialist_agents.quant_agent import quant_agent
from app.monitors import create_monitor
from app.core.config import Settings

load_dotenv(".env", override=True)

# Initialize ModelMonitor
settings = Settings()
monitor = create_monitor(settings, settings.monitoring_provider)
monitor.initialize()

@pytest.mark.asyncio
async def test_quant_agent():
    """Test Quant Agent với query đơn giản"""
    query = "Phân tích định lượng cổ phiếu VIC - tính RSI, MACD và moving averages"
    
    try:
        result = await Runner.run(quant_agent, query)
        
        print(f"Agent: {quant_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'symbol')
        assert hasattr(result.final_output, 'analysis_type')
        print("✅ Quant agent test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_quant_agent_success", {
                "agent": quant_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__
            })
        
    except Exception as e:
        print(f"❌ Quant agent test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_quant_agent_failure", {
                "agent": quant_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


if __name__ == "__main__":
    asyncio.run(test_quant_agent())
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed traces to monitoring provider")
    
    monitor.shutdown()
