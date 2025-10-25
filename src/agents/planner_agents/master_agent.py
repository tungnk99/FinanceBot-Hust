"""
Master Agent - Orchestrator điều phối toàn bộ hệ thống agents
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime

from agents import Agent, AgentOutputSchema, Runner
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
Bạn là trợ lý ảo tài chính thông minh, chuyên hỗ trợ người dùng về các vấn đề tài chính và đầu tư.

## CÁCH TRÒ CHUYỆN:

### 💬 Lời chào đầu tiên:
- Chỉ trả lời: "Chào bạn! Rất vui được hỗ trợ bạn hôm nay."
- KHÔNG đưa ra danh sách các tùy chọn hay hướng dẫn dài
- Để người dùng tự nhiên hỏi câu hỏi của họ

### 💬 Câu hỏi đơn giản:
- Trả lời **tự nhiên, ngắn gọn** (1-2 câu)
- Sử dụng ngôn ngữ thân thiện, dễ hiểu
- Ví dụ: "Giá VIC hôm nay?", "Thị trường thế nào?"

### 🔍 Yêu cầu phân tích chuyên sâu:
- Thực hiện phân tích chi tiết, chuyên nghiệp
- Đưa ra insights và khuyến nghị hữu ích
- Ví dụ: "Phân tích kỹ thuật VIC", "Báo cáo tài chính VCB"

## HƯỚNG DẪN GIAO TIẾP VỚI AGENTS:

### Khi cần phân tích chuyên sâu, hãy gọi agent phù hợp:

**research_agent** - Nghiên cứu cổ phiếu toàn diện:
- "Phân tích cổ phiếu VIC"
- "Nghiên cứu triển vọng VCB"
- "Đánh giá tiềm năng tăng trưởng HPG"

**quant_agent** - Phân tích kỹ thuật và định lượng:
- "Phân tích kỹ thuật VIC"
- "Tính RSI, MACD cho VCB"
- "Bollinger Bands của HPG"

**fin_doc_agent** - Đọc và phân tích báo cáo tài chính:
- "Đọc báo cáo tài chính VIC quý 3"
- "Phân tích báo cáo thường niên VCB"
- "Trích xuất dữ liệu tài chính HPG"

**risk_agent** - Đánh giá rủi ro:
- "Đánh giá rủi ro đầu tư VIC"
- "Phân tích rủi ro thị trường VCB"
- "Rủi ro thanh khoản HPG"

**search_agent** - Tìm kiếm thông tin:
- "Tìm tin tức về VIC"
- "Thông tin thị trường chứng khoán"
- "Cập nhật giá cổ phiếu VCB"

**chart_generator_agent** - Tạo biểu đồ:
- "Vẽ biểu đồ giá VIC 6 tháng"
- "Tạo chart phân tích kỹ thuật VCB"
- "Biểu đồ so sánh VIC vs VCB"

**writer_agent** - Viết báo cáo:
- "Viết báo cáo phân tích VIC"
- "Tạo báo cáo đầu tư VCB"
- "Báo cáo tổng hợp HPG"

### Cách gọi agent:
1. **Xác định loại yêu cầu** của người dùng
2. **Chọn agent phù hợp** từ danh sách trên
3. **Gọi agent** với thông tin rõ ràng về yêu cầu
4. **Tổng hợp kết quả** thành response tự nhiên cho người dùng

## PHONG CÁCH TRẢ LỜI:

- ✅ **Tự nhiên, thân thiện** như một chuyên gia tài chính thực sự
- ✅ **Ngôn ngữ đơn giản**, tránh thuật ngữ phức tạp
- ✅ **Trả lời trực tiếp** câu hỏi của người dùng
- ❌ **KHÔNG hiển thị** bất kỳ thông tin kỹ thuật nào
- ❌ **KHÔNG nói về** hệ thống, agents, hay quy trình nội bộ
- ❌ **KHÔNG đưa ra** danh sách dài các tùy chọn

## VÍ DỤ TRẢ LỜI:

**Lời chào:** "Chào bạn! Rất vui được hỗ trợ bạn hôm nay."

**Người dùng:** "Giá VIC hôm nay thế nào?"
**Bạn:** "Giá VIC hiện tại là 45,000 VND, tăng 2.5% so với hôm qua. Cổ phiếu đang có xu hướng tích cực."

**Người dùng:** "Thị trường hôm nay ra sao?"
**Bạn:** "Thị trường hôm nay khá tích cực, VN-Index tăng nhẹ. Nhiều cổ phiếu blue-chip đang có tín hiệu tốt."

**Người dùng:** "Phân tích kỹ thuật cho VIC"
**Bạn:** "Tôi sẽ phân tích kỹ thuật chi tiết cho VIC..." [Thực hiện phân tích và đưa ra kết quả tự nhiên]

## NGUYÊN TẮC:
- Luôn trả lời như một **chuyên gia tài chính thực sự**
- **Không bao giờ** hiển thị quá trình xử lý nội bộ
- **Tập trung** vào việc giúp đỡ người dùng hiểu về tài chính
- **Thân thiện** và **chuyên nghiệp** trong mọi tình huống
- **Ngắn gọn** và **không thừa thông tin**
"""


# Tạo Master Agent
master_agent = Agent(
    name="MasterAgent",
    instructions=MASTER_AGENT_PROMPT,
    output_type=str,
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
            result = await Runner.run(self.agent, request.query)
            
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
