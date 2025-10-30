from pydantic import BaseModel
from typing import Any, Dict, List
from agents import Agent, AgentOutputSchema
from agent_libs.setting import settings
from agent_libs.logging import setup_langfuse, is_langfuse_ready
from agent_libs.tools.stock_market import get_realtime_market_data
from agent_libs.tools.crypto_market import get_crypto_market_data

# Setup Langfuse if available
setup_langfuse()


# Financial Search Agent specializing in comprehensive financial research
SEARCH_PROMPT = (
    "Bạn là một trợ lý nghiên cứu tài chính chuyên nghiệp có nhiệm vụ là tìm kiếm thông tin tài chính.\n\n"
    
    "NHIỆM VỤ CỦA BẠN:\n"
    "1. Nhận yêu cầu tìm kiếm thông tin tài chính\n"
    "2. Truy vấn dữ liệu từ các nguồn phù hợp\n"
    "3. Tổng hợp và trả về thông tin hoàn chỉnh\n\n"
    
    "CÔNG CỤ CÓ SẴN:\n"
    "- get_realtime_market_data: Lấy dữ liệu chứng khoán Việt Nam (HOSE, HNX, UPCOM)\n"
    "- get_crypto_market_data: Lấy dữ liệu thị trường tiền điện tử\n\n"
    
    "QUY TRÌNH XỬ LÝ:\n"
    "1. Phân tích yêu cầu để xác định loại dữ liệu cần thiết\n"
    "2. Gọi tool phù hợp DUY NHẤT MỘT LẦN với tham số chính xác\n"
    "3. Tổng hợp dữ liệu nhận được\n"
    "4. Trả về kết quả có cấu trúc rõ ràng\n\n"
    
    "QUAN TRỌNG:\n"
    "- KHÔNG gọi lại cùng một tool với cùng tham số\n"
    "- Sử dụng đúng tool cho đúng loại dữ liệu\n"
    "- Trả về thông tin chính xác và có căn cứ\n"
    "- Cấu trúc kết quả theo format SearchResult"
)


class SearchResult(BaseModel):
    """Search result output"""
    query: str
    """Search query"""
    results: List[Dict[str, Any]]
    """Search results"""
    summary: str
    """Summary of findings"""
    key_insights: List[str]
    """Key insights from search"""
    data_sources: List[str]
    """Data sources used"""
    timestamp: str
    """Search timestamp"""
    confidence_score: float
    """Confidence score (0-1)"""
    
    pass


search_agent = Agent(
    name="FinancialSearchAgent",
    instructions=SEARCH_PROMPT,
    output_type=AgentOutputSchema(SearchResult, strict_json_schema=False),
    tools=[
        get_realtime_market_data,
        get_crypto_market_data
    ],
    model=settings.OPENAI_MODEL
)