import asyncio
import pytest
from dotenv import load_dotenv
from agents import Runner
from src.agents.task_agents.search_agent import search_agent
from app.monitors import create_monitor
from app.core.config import Settings

load_dotenv(".env", override=True)

import nest_asyncio
nest_asyncio.apply()

# Initialize ModelMonitor
settings = Settings()
monitor = create_monitor(settings, settings.monitoring_provider)
monitor.initialize()



@pytest.mark.asyncio
async def test_search_agent():
    """Test Search Agent với query đơn giản"""
    query = "Tìm kiếm thông tin về cổ phiếu VIC trên thị trường chứng khoán Việt Nam"
    
    try:
        result = await Runner.run(search_agent, query)
        
        print(f"Agent: {search_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'query')
        assert hasattr(result.final_output, 'summary')
        print("✅ Search agent test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_search_agent_success", {
                "agent": search_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__
            })
        
    except Exception as e:
        print(f"❌ Search agent test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_search_agent_failure", {
                "agent": search_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


if __name__ == "__main__":
    asyncio.run(test_search_agent())
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed traces to monitoring provider")
    
    monitor.shutdown()
