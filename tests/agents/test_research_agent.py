import asyncio
import pytest
from dotenv import load_dotenv
from agents import Runner
from src.agents.specialist_agents.research_agent import research_agent
from app.monitors import create_monitor
from app.core.config import Settings

load_dotenv(".env", override=True)

# Initialize ModelMonitor
settings = Settings()
monitor = create_monitor(settings, settings.monitoring_provider)
monitor.initialize()

@pytest.mark.asyncio
async def test_research_agent():
    """Test Research Agent với query đơn giản"""
    query = "Nghiên cứu cổ phiếu VIC - phân tích cơ bản và thị trường"
    
    try:
        result = await Runner.run(research_agent, query)
        
        print(f"Agent: {research_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'symbol')
        assert hasattr(result.final_output, 'analysis_summary')
        print("✅ Research agent test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_research_agent_success", {
                "agent": research_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__
            })
        
    except Exception as e:
        print(f"❌ Research agent test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_research_agent_failure", {
                "agent": research_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


if __name__ == "__main__":
    asyncio.run(test_research_agent())
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed traces to monitoring provider")
    
    monitor.shutdown()
