import asyncio
import pytest
from dotenv import load_dotenv
from agents import Runner
from src.agents.specialist_agents.fin_doc_agent import fin_doc_agent
from app.monitors import create_monitor
from app.core.config import Settings

load_dotenv(".env", override=True)

# Initialize ModelMonitor
settings = Settings()
monitor = create_monitor(settings, settings.monitoring_provider)
monitor.initialize()

@pytest.mark.asyncio
async def test_fin_doc_agent():
    """Test Fin Doc Agent với query đơn giản"""
    query = "Phân tích báo cáo tài chính của VIC năm 2023"
    
    try:
        result = await Runner.run(fin_doc_agent, query)
        
        print(f"Agent: {fin_doc_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'company_name')
        assert hasattr(result.final_output, 'analysis_summary')
        print("✅ Fin doc agent test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_fin_doc_agent_success", {
                "agent": fin_doc_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__
            })
        
    except Exception as e:
        print(f"❌ Fin doc agent test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_fin_doc_agent_failure", {
                "agent": fin_doc_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


if __name__ == "__main__":
    asyncio.run(test_fin_doc_agent())
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed traces to monitoring provider")
    
    monitor.shutdown()
