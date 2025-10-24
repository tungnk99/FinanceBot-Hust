import asyncio
import pytest
from dotenv import load_dotenv
from agents import Runner
from src.agents.task_agents.chart_generator_agent import chart_generator_agent
from app.monitors import create_monitor
from app.core.config import Settings

load_dotenv(".env", override=True)

# Initialize ModelMonitor
settings = Settings()
monitor = create_monitor(settings, settings.monitoring_provider)
monitor.initialize()

@pytest.mark.asyncio
async def test_chart_generator_agent():
    """Test Chart Generator Agent với query đơn giản"""
    query = "Tạo biểu đồ giá cổ phiếu VIC trong 6 tháng qua với moving averages"
    
    try:
        result = await Runner.run(chart_generator_agent, query)
        
        print(f"Agent: {chart_generator_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'chart_type')
        assert hasattr(result.final_output, 'title')
        print("✅ Chart generator agent test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_chart_generator_agent_success", {
                "agent": chart_generator_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__
            })
        
    except Exception as e:
        print(f"❌ Chart generator agent test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_chart_generator_agent_failure", {
                "agent": chart_generator_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


if __name__ == "__main__":
    asyncio.run(test_chart_generator_agent())
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed traces to monitoring provider")
    
    monitor.shutdown()
