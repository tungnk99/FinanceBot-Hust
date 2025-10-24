import asyncio
import pytest
from dotenv import load_dotenv
from agents import Runner
from src.agents.planner_agents.master_agent import master_agent, MasterAgentRequest, QueryType, Priority
from app.monitors import create_monitor
from app.core.config import Settings

load_dotenv(".env", override=True)

# Initialize ModelMonitor
settings = Settings()
monitor = create_monitor(settings, settings.monitoring_provider)
monitor.initialize()

@pytest.mark.asyncio
async def test_master_agent_stock_research():
    """Test Master Agent với stock research query"""
    query = "Phân tích cổ phiếu VIC - nghiên cứu toàn diện về công ty và triển vọng đầu tư"
    
    try:
        result = await Runner.run(master_agent, query)
        
        print(f"Agent: {master_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'query')
        assert hasattr(result.final_output, 'selected_agent')
        assert hasattr(result.final_output, 'success')
        print("✅ Master agent stock research test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_master_agent_stock_research_success", {
                "agent": master_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__,
                "success": result.final_output.success
            })
        
    except Exception as e:
        print(f"❌ Master agent stock research test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_master_agent_stock_research_failure", {
                "agent": master_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


@pytest.mark.asyncio
async def test_master_agent_quantitative_analysis():
    """Test Master Agent với quantitative analysis query"""
    query = "Tính RSI, MACD và Moving Averages cho cổ phiếu AAPL"
    
    try:
        result = await Runner.run(master_agent, query)
        
        print(f"Agent: {master_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'query')
        assert hasattr(result.final_output, 'selected_agent')
        assert hasattr(result.final_output, 'success')
        print("✅ Master agent quantitative analysis test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_master_agent_quant_analysis_success", {
                "agent": master_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__,
                "success": result.final_output.success
            })
        
    except Exception as e:
        print(f"❌ Master agent quantitative analysis test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_master_agent_quant_analysis_failure", {
                "agent": master_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


@pytest.mark.asyncio
async def test_master_agent_chart_generation():
    """Test Master Agent với chart generation query"""
    query = "Tạo biểu đồ giá cổ phiếu VIC với moving averages và Bollinger Bands"
    
    try:
        result = await Runner.run(master_agent, query)
        
        print(f"Agent: {master_agent.name}")
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'query')
        assert hasattr(result.final_output, 'selected_agent')
        assert hasattr(result.final_output, 'success')
        print("✅ Master agent chart generation test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_master_agent_chart_generation_success", {
                "agent": master_agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__,
                "success": result.final_output.success
            })
        
    except Exception as e:
        print(f"❌ Master agent chart generation test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_master_agent_chart_generation_failure", {
                "agent": master_agent.name,
                "query": query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


@pytest.mark.asyncio
async def test_master_agent_with_request_model():
    """Test Master Agent với MasterAgentRequest model"""
    request = MasterAgentRequest(
        query="Viết báo cáo phân tích tài chính cho cổ phiếu MSFT",
        query_type=QueryType.REPORT_WRITING,
        priority=Priority.HIGH,
        context={"company": "Microsoft", "sector": "Technology"},
        user_id="test_user",
        session_id="test_session"
    )
    
    try:
        # Test với request model
        result = await Runner.run(master_agent, request.query)
        
        print(f"Agent: {master_agent.name}")
        print(f"Request: {request}")
        print(f"Result: {result.final_output}")
        print("-" * 50)
        
        # Verify result structure
        assert hasattr(result.final_output, 'query')
        assert hasattr(result.final_output, 'selected_agent')
        assert hasattr(result.final_output, 'success')
        print("✅ Master agent with request model test passed!")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event("test_master_agent_request_model_success", {
                "agent": master_agent.name,
                "query": request.query,
                "query_type": request.query_type.value,
                "priority": request.priority.value,
                "result_type": type(result.final_output).__name__,
                "success": result.final_output.success
            })
        
    except Exception as e:
        print(f"❌ Master agent with request model test failed: {e}")
        # Log test failure
        if monitor.is_configured:
            monitor.log_event("test_master_agent_request_model_failure", {
                "agent": master_agent.name,
                "query": request.query,
                "error": str(e)
            })
        raise
    
    finally:
        # Flush traces after test
        if monitor.is_configured:
            monitor.flush()


if __name__ == "__main__":
    asyncio.run(test_master_agent_stock_research())
    print("\n" + "="*60 + "\n")
    asyncio.run(test_master_agent_quantitative_analysis())
    print("\n" + "="*60 + "\n")
    asyncio.run(test_master_agent_chart_generation())
    print("\n" + "="*60 + "\n")
    asyncio.run(test_master_agent_with_request_model())
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed traces to monitoring provider")
    
    monitor.shutdown()
