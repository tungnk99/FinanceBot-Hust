#!/usr/bin/env python3
"""
Run all agent tests with proper setup and ModelMonitor integration
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from agents import Runner, Agent
from agents.extensions.models.litellm_model import LitellmModel

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

load_dotenv(".env", override=True)

# Import settings and monitoring
from src.setting import settings
from app.monitors import create_monitor
from app.core.config import Settings

# Initialize ModelMonitor
app_settings = Settings()
monitor = create_monitor(app_settings, app_settings.monitoring_provider)
monitor.initialize()

# Test queries for each agent
TEST_QUERIES = {
    "fin_doc_agent": "Phân tích báo cáo tài chính của VIC năm 2023",
    "quant_agent": "Phân tích định lượng cổ phiếu VIC - tính RSI, MACD và moving averages", 
    "research_agent": "Nghiên cứu cổ phiếu VIC - phân tích cơ bản và thị trường",
    "risk_agent": "Đánh giá rủi ro đầu tư vào cổ phiếu VIC",
    "search_agent": "Tìm kiếm thông tin về cổ phiếu VIC trên thị trường chứng khoán Việt Nam",
    "chart_generator_agent": "Tạo biểu đồ giá cổ phiếu VIC trong 6 tháng qua với moving averages",
    "writer_agent": "Viết báo cáo phân tích tài chính chuyên nghiệp cho cổ phiếu VIC",
    "integrated_report_agent": "Tạo báo cáo tài chính tích hợp toàn diện cho cổ phiếu VIC với biểu đồ và phân tích"
}

async def test_agent(agent_name, agent, query):
    """Test a single agent with monitoring"""
    print(f"\n🧪 Testing {agent_name}...")
    print(f"📝 Query: {query}")
    print(f"🤖 Agent: {agent.name}")
    print("-" * 60)
    
    try:
        result = await Runner.run(agent, query)
        print(f"✅ SUCCESS: {str(result.final_output)[:200]}...")
        
        # Log test success
        if monitor.is_configured:
            monitor.log_event(f"test_{agent_name}_success", {
                "agent": agent.name,
                "query": query,
                "result_type": type(result.final_output).__name__,
                "success": True
            })
            monitor.flush()
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:200]}...")
        
        # Log test failure
        if monitor.is_configured:
            monitor.log_event(f"test_{agent_name}_failure", {
                "agent": agent.name,
                "query": query,
                "error": str(e),
                "success": False
            })
            monitor.flush()
        
        return False

async def run_all_tests():
    """Run all agent tests with monitoring"""
    print("🚀 Starting FinanceBot Agent Tests")
    print("=" * 60)
    
    # Log test session start
    if monitor.is_configured:
        monitor.log_event("test_session_start", {
            "total_agents": len(TEST_QUERIES),
            "monitoring_provider": app_settings.monitoring_provider
        })
        monitor.flush()
    
    # Import all agents
    try:
        from src.agents.specialist_agents.fin_doc_agent import fin_doc_agent
        from src.agents.specialist_agents.quant_agent import quant_agent
        from src.agents.specialist_agents.research_agent import research_agent
        from src.agents.specialist_agents.risk_agent import risk_agent
        from src.agents.task_agents.search_agent import search_agent
        from src.agents.task_agents.chart_generator_agent import chart_generator_agent
        from src.agents.task_agents.writer_agent import writer_agent
        from src.agents.task_agents.integrated_report_agent import integrated_report_agent
        
        agents = {
            "fin_doc_agent": fin_doc_agent,
            "quant_agent": quant_agent,
            "research_agent": research_agent,
            "risk_agent": risk_agent,
            "search_agent": search_agent,
            "chart_generator_agent": chart_generator_agent,
            "writer_agent": writer_agent,
            "integrated_report_agent": integrated_report_agent
        }
        
        print(f"✅ Successfully imported {len(agents)} agents")
        
    except Exception as e:
        print(f"❌ Failed to import agents: {e}")
        return
    
    # Test each agent
    success_count = 0
    total_count = len(agents)
    
    for agent_name, agent in agents.items():
        query = TEST_QUERIES.get(agent_name, "Test query")
        success = await test_agent(agent_name, agent, query)
        if success:
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {success_count}/{total_count} agents passed")
    
    # Log test session summary
    if monitor.is_configured:
        monitor.log_event("test_session_complete", {
            "total_agents": total_count,
            "successful_agents": success_count,
            "failed_agents": total_count - success_count,
            "success_rate": success_count / total_count if total_count > 0 else 0
        })
        monitor.log_metric("test_success_rate", success_count / total_count if total_count > 0 else 0)
        monitor.flush()
    
    if success_count == total_count:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")
    
    # Final flush and shutdown
    if monitor.is_configured:
        monitor.flush()
        print("✅ Flushed all traces to monitoring provider")
        monitor.shutdown()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
