"""
Task Agent Tools - Sử dụng agents as tools cho specialist agents
"""
from .task_agents.search_agent import search_agent
from .task_agents.chart_generator_agent import chart_generator_agent
from .task_agents.writer_agent import writer_agent
from .specialist_agents.quant_agent import quant_agent

# Task Agent Tools sử dụng agent.as_tool() pattern
search_agent_tool = search_agent.as_tool(
    tool_name="search_expert",
    tool_description="Tìm kiếm thông tin tài chính, tin tức và dữ liệu thị trường từ nhiều nguồn"
)

chart_generator_agent_tool = chart_generator_agent.as_tool(
    tool_name="chart_expert", 
    tool_description="Tạo biểu đồ tài chính chuyên nghiệp và visualizations"
)

quant_agent_tool = quant_agent.as_tool(
    tool_name="quant_expert",
    tool_description="Phân tích định lượng, kỹ thuật và tính toán các metrics tài chính"
)

writer_agent_tool = writer_agent.as_tool(
    tool_name="writer_expert",
    tool_description="Viết báo cáo tài chính chuyên nghiệp và comprehensive analysis"
)

# Lazy import for risk_agent to avoid circular import
def get_risk_agent_tool():
    from .specialist_agents.risk_agent import risk_agent
    return risk_agent.as_tool(
        tool_name="risk_expert",
        tool_description="Đánh giá rủi ro toàn diện và phân tích các yếu tố rủi ro"
    )

# Export all task agent tools (without risk_agent_tool to avoid circular import)
TASK_AGENT_TOOLS = [
    search_agent_tool,
    chart_generator_agent_tool,
    quant_agent_tool,
    writer_agent_tool
]

# Function to get all tools including risk_agent_tool when needed
def get_all_task_agent_tools():
    """Get all task agent tools including risk_agent_tool"""
    return TASK_AGENT_TOOLS + [get_risk_agent_tool()]
