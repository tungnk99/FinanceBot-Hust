import asyncio
import pytest
from dotenv import load_dotenv
from agents import Runner
from src.agents.specialist_agents.risk_agent import risk_agent
from app.monitors import create_monitor
from app.core.config import Settings

load_dotenv(".env", override=True)

# Initialize ModelMonitor
settings = Settings()
monitor = create_monitor(settings, settings.monitoring_provider)
monitor.initialize()

@pytest.mark.asyncio
async def test_risk_agent():
    """Test Risk Agent với query đơn giản"""
    query = "Đánh giá rủi ro đầu tư vào cổ phiếu VIC"
    
    try:
        result = await Runner.run(risk_agent, query)
        
        print(f"Agent: {risk_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'summary')
        print("✅ Risk agent test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_risk_agent_success", {
                "agent": risk_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__
            })
        
    except Exception as e:
        print(f"❌ Risk agent test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_risk_agent_failure", {
                "agent": risk_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


if __name__ == "__main__":
    asyncio.run(test_risk_agent())
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed traces to monitoring provider")
    
    monitor.shutdown()
