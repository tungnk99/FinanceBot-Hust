"""
Master Agent - Orchestrator điều phối toàn bộ hệ thống agents
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime

from agents import Agent, AgentOutputSchema
from src.setting import settings

# Import tất cả specialist agents
from ..specialist_agents.research_agent import research_agent
from ..specialist_agents.quant_agent import quant_agent
from ..specialist_agents.fin_doc_agent import fin_doc_agent
from ..specialist_agents.risk_agent import risk_agent

# Import tất cả task agents
from ..task_agents.search_agent import search_agent
from ..task_agents.chart_generator_agent import chart_generator_agent
from ..task_agents.writer_agent import writer_agent
# from ..task_agents.integrated_report_agent import integrated_report_agent  # Not available

# Import direct tools
from ...tools.stock_market import get_realtime_market_data
from ...tools.crypto_market import get_crypto_market_data
from ...tools.retrieval_tool import retrieval_tool
from ...tools.yfinance_data import get_stock_with_technical_analysis


class QueryType(str, Enum):
    """Các loại query mà Master Agent có thể xử lý"""
    STOCK_RESEARCH = "stock_research"
    QUANTITATIVE_ANALYSIS = "quantitative_analysis"
    FINANCIAL_DOCUMENT = "financial_document"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_SEARCH = "market_search"
    CHART_GENERATION = "chart_generation"
    REPORT_WRITING = "report_writing"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    GENERAL_FINANCE = "general_finance"


class Priority(str, Enum):
    """Mức độ ưu tiên của request"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MasterAgentRequest(BaseModel):
    """Request model cho Master Agent"""
    query: str = Field(..., description="Câu hỏi hoặc yêu cầu của người dùng")
    query_type: Optional[QueryType] = Field(default=None, description="Loại query (tự động detect nếu không chỉ định)")
    priority: Priority = Field(default=Priority.MEDIUM, description="Mức độ ưu tiên")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Context bổ sung")
    user_id: Optional[str] = Field(default=None, description="ID người dùng")
    session_id: Optional[str] = Field(default=None, description="ID session")


class AgentSelection(BaseModel):
    """Thông tin về agent được chọn"""
    agent_name: str
    agent_type: str  # "specialist" hoặc "task"
    confidence_score: float
    reasoning: str
    estimated_time: Optional[float] = Field(default=None)  # seconds (can be fractional)


class MasterAgentResponse(BaseModel):
    """Response model cho Master Agent"""
    request_id: str
    query: str
    query_type: QueryType
    selected_agent: AgentSelection
    execution_result: Any
    execution_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = Field(default=None)
    follow_up_suggestions: Optional[List[str]] = Field(default_factory=list)


# Master Agent Instructions
MASTER_AGENT_PROMPT = """
Bạn là Master Agent - Orchestrator điều phối toàn bộ hệ thống FinanceBot. Nhiệm vụ của bạn là:

## Chức năng chính:
1. **Phân tích query**: Hiểu rõ yêu cầu của người dùng
2. **Chọn agent phù hợp**: Lựa chọn specialist agent hoặc task agent tốt nhất
3. **Điều phối execution**: Gọi agent được chọn và xử lý kết quả
4. **Tổng hợp response**: Trả về kết quả hoàn chỉnh và gợi ý follow-up

## Các agents có sẵn:

### Specialist Agents:
- **research_agent**: Nghiên cứu cổ phiếu toàn diện (phân tích cơ bản, kỹ thuật, thị trường)
- **quant_agent**: Phân tích định lượng (RSI, MACD, Bollinger Bands, P/E ratios)
- **fin_doc_agent**: Đọc và phân tích báo cáo tài chính
- **risk_agent**: Đánh giá rủi ro và phân tích risk factors

### Task Agents:
- **search_agent**: Tìm kiếm thông tin tài chính từ nhiều nguồn
- **chart_generator_agent**: Tạo biểu đồ tài chính chuyên nghiệp
- **writer_agent**: Viết báo cáo tài chính chuyên nghiệp

### Direct Tools:
- **get_realtime_market_data**: Dữ liệu thị trường chứng khoán VN
- **get_crypto_market_data**: Dữ liệu tiền điện tử
- **get_stock_with_technical_analysis**: Lấy dữ liệu + tính technical indicators từ yfinance
- **retrieval_tool**: Tìm kiếm thông tin tổng quát

## Quy tắc lựa chọn agent:

### Cho Stock Research:
- Query về phân tích cổ phiếu → **research_agent**
- Query về technical analysis → **quant_agent**
- Query về risk assessment → **risk_agent**

### Cho Financial Documents:
- Query về báo cáo tài chính → **fin_doc_agent**
- Query về document analysis → **fin_doc_agent**

### Cho Market Data:
- Query về market data → **search_agent** hoặc direct tools
- Query về crypto → **get_crypto_market_data**

### Cho Visualizations:
- Query về charts → **chart_generator_agent**
- Query về visualizations → **chart_generator_agent**

### Cho Reports:
- Query về writing reports → **writer_agent**
- Query về comprehensive reports → **writer_agent**

### Cho General Finance:
- Query chung về tài chính → **search_agent** hoặc **research_agent**

## Workflow:
1. Phân tích query và xác định query_type
2. Chọn agent phù hợp nhất với confidence score
3. Gọi agent được chọn
4. Xử lý và tổng hợp kết quả
5. Đưa ra gợi ý follow-up

## Response Format:
- Luôn cung cấp reasoning cho việc chọn agent
- Đưa ra confidence score (0-1)
- Cung cấp execution time
- Đề xuất follow-up questions
- Xử lý errors gracefully

Luôn ưu tiên accuracy và user experience. Đảm bảo response nhanh chóng và chính xác.
"""


# Tạo Master Agent
master_agent = Agent(
    name="MasterAgent",
    instructions=MASTER_AGENT_PROMPT,
    output_type=AgentOutputSchema(MasterAgentResponse, strict_json_schema=False),
    tools=[
        # Specialist agents as tools
        research_agent.as_tool(
            tool_name="research_expert",
            tool_description="Nghiên cứu cổ phiếu toàn diện với phân tích cơ bản, kỹ thuật và thị trường"
        ),
        quant_agent.as_tool(
            tool_name="quant_expert", 
            tool_description="Phân tích định lượng, kỹ thuật và tính toán các metrics tài chính"
        ),
        fin_doc_agent.as_tool(
            tool_name="fin_doc_expert",
            tool_description="Đọc và phân tích báo cáo tài chính, trích xuất dữ liệu"
        ),
        risk_agent.as_tool(
            tool_name="risk_expert",
            tool_description="Đánh giá rủi ro toàn diện và phân tích các yếu tố rủi ro"
        ),
        # Task agents as tools
        search_agent.as_tool(
            tool_name="search_expert",
            tool_description="Tìm kiếm thông tin tài chính từ nhiều nguồn dữ liệu"
        ),
        chart_generator_agent.as_tool(
            tool_name="chart_expert",
            tool_description="Tạo biểu đồ tài chính chuyên nghiệp và visualizations"
        ),
        writer_agent.as_tool(
            tool_name="writer_expert",
            tool_description="Viết báo cáo tài chính chuyên nghiệp và comprehensive analysis"
        ),
        # Direct tools
        get_realtime_market_data,
        get_crypto_market_data,
        get_stock_with_technical_analysis,
        retrieval_tool
    ],
    model=settings.OPENAI_MODEL,
)


# Helper functions cho Master Agent
class MasterAgentOrchestrator:
    """Helper class cho Master Agent orchestration"""
    
    def __init__(self):
        self.agent = master_agent
        self.agent_registry = {
            "research_agent": research_agent,
            "quant_agent": quant_agent,
            "fin_doc_agent": fin_doc_agent,
            "risk_agent": risk_agent,
            "search_agent": search_agent,
            "chart_generator_agent": chart_generator_agent,
            "writer_agent": writer_agent
        }
    
    async def process_request(self, request: MasterAgentRequest) -> MasterAgentResponse:
        """Xử lý request và trả về response"""
        import uuid
        import time
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Gọi Master Agent
            result = await self.agent.run(request.query)
            
            execution_time = time.time() - start_time
            
            return MasterAgentResponse(
                request_id=request_id,
                query=request.query,
                query_type=request.query_type or QueryType.GENERAL_FINANCE,
                selected_agent=AgentSelection(
                    agent_name="auto_selected",
                    agent_type="specialist",
                    confidence_score=0.9,
                    reasoning="Auto-selected by Master Agent",
                    estimated_time=execution_time
                ),
                execution_result=result,
                execution_time=execution_time,
                timestamp=datetime.now(),
                success=True,
                follow_up_suggestions=self._generate_follow_up_suggestions(request.query)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return MasterAgentResponse(
                request_id=request_id,
                query=request.query,
                query_type=request.query_type or QueryType.GENERAL_FINANCE,
                selected_agent=AgentSelection(
                    agent_name="error",
                    agent_type="error",
                    confidence_score=0.0,
                    reasoning="Error occurred during processing",
                    estimated_time=execution_time
                ),
                execution_result=None,
                execution_time=execution_time,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e),
                follow_up_suggestions=[]
            )
    
    def _generate_follow_up_suggestions(self, query: str) -> List[str]:
        """Tạo gợi ý follow-up dựa trên query"""
        suggestions = []
        
        query_lower = query.lower()
        
        if "vic" in query_lower or "vcb" in query_lower or "hpg" in query_lower:
            suggestions.extend([
                "Bạn có muốn phân tích kỹ thuật chi tiết hơn không?",
                "Có cần đánh giá rủi ro cho cổ phiếu này không?",
                "Bạn có muốn so sánh với các cổ phiếu khác trong ngành không?"
            ])
        
        if "báo cáo" in query_lower or "tài chính" in query_lower:
            suggestions.extend([
                "Bạn có muốn tạo biểu đồ minh họa không?",
                "Có cần phân tích xu hướng dài hạn không?",
                "Bạn có muốn so sánh với các kỳ trước không?"
            ])
        
        if "rủi ro" in query_lower or "risk" in query_lower:
            suggestions.extend([
                "Bạn có muốn phân tích rủi ro chi tiết hơn không?",
                "Có cần đánh giá rủi ro thị trường không?",
                "Bạn có muốn tìm hiểu cách giảm thiểu rủi ro không?"
            ])
        
        # Default suggestions
        if not suggestions:
            suggestions.extend([
                "Bạn có câu hỏi nào khác về tài chính không?",
                "Có cần phân tích sâu hơn về chủ đề này không?",
                "Bạn có muốn tìm hiểu về các chủ đề liên quan không?"
            ])
        
        return suggestions[:3]  # Trả về tối đa 3 gợi ý


# Export
__all__ = [
    "master_agent",
    "MasterAgentOrchestrator", 
    "MasterAgentRequest",
    "MasterAgentResponse",
    "AgentSelection",
    "QueryType",
    "Priority"
]
