import asyncio
import pytest
from dotenv import load_dotenv
from agents import Runner
from src.agents.task_agents.writer_agent import writer_agent
from app.monitors import create_monitor
from app.core.config import Settings

load_dotenv(".env", override=True)

# Initialize ModelMonitor
settings = Settings()
monitor = create_monitor(settings, settings.monitoring_provider)
monitor.initialize()

@pytest.mark.asyncio
async def test_writer_agent():
    """Test Writer Agent với query đơn giản"""
    query = "Viết báo cáo phân tích tài chính chuyên nghiệp cho cổ phiếu VIC"
    
    try:
        result = await Runner.run(writer_agent, query)
        
        print(f"Agent: {writer_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        print("✅ Writer agent test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_writer_agent_success", {
                "agent": writer_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__
            })
        
    except Exception as e:
        print(f"❌ Writer agent test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_writer_agent_failure", {
                "agent": writer_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


if __name__ == "__main__":
    asyncio.run(test_writer_agent())
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed traces to monitoring provider")
    
    monitor.shutdown()
