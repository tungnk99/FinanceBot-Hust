import datetime
from pydantic import BaseModel
from typing import Any, Dict, List
from agents import Agent, AgentOutputSchema, WebSearchTool, function_tool
from agent_libs.setting import settings
from agent_libs.logging import setup_langfuse
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
    "- get_crypto_market_data: Lấy dữ liệu thị trường tiền điện tử\n"
    "- WebSearchTool (OpenAI Web Search): Tìm kiếm tổng hợp từ web/news/APIs\n\n"
    
    "QUY TRÌNH XỬ LÝ:\n"
    "1. Phân tích yêu cầu để xác định loại dữ liệu cần thiết\n"
    "2. XÁC ĐỊNH THỜI ĐIỂM TÌM KIẾM: nếu người dùng không nêu rõ, mặc định là 'hôm nay' theo múi giờ Việt Nam (Asia/Ho_Chi_Minh). Trước khi tìm kiếm, HÃY GỌI tool get_time_now để lấy thời điểm hiện tại, rồi suy ra mốc thời gian tương ứng (hôm nay/hôm qua/tuần này/tháng này) và CHÈN mốc thời gian vào truy vấn.\n"
    "3. Gọi tool phù hợp DUY NHẤT MỘT LẦN với tham số chính xác (bao gồm mốc thời gian đã xác định).\n"
    "3. Tổng hợp dữ liệu nhận được\n"
    "4. Trả về kết quả có cấu trúc rõ ràng\n\n"
    
    "QUAN TRỌNG:\n"
    "- KHÔNG gọi lại cùng một tool với cùng tham số\n"
    "- Sử dụng đúng tool cho đúng loại dữ liệu\n"
    "- Trả về thông tin chính xác và có căn cứ\n"
    "- LUÔN ưu tiên dữ liệu theo đúng mốc thời gian người dùng yêu cầu; nếu người dùng nói 'hôm nay', chỉ tổng hợp thông tin của NGÀY HÔM NAY. Với tìm kiếm web, thêm bộ lọc/ngữ cảnh thời gian phù hợp (ví dụ: today, past 24h, ngày YYYY-MM-DD).\n"
    "- Trong phần summary, nêu rõ khung thời gian dữ liệu (ví dụ: 'Dữ liệu ngày YYYY-MM-DD theo Asia/Ho_Chi_Minh').\n"
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


@function_tool
async def get_time_now() -> str:
    """Get time now"""
    return "Time now is " + datetime.datetime.now().isoformat()


search_agent = Agent(
    name="FinancialSearchAgent",
    instructions=SEARCH_PROMPT,
    output_type=AgentOutputSchema(SearchResult, strict_json_schema=False),
    tools=[
        get_realtime_market_data,
        get_crypto_market_data,
        WebSearchTool(),
        get_time_now
    ],
    model=settings.OPENAI_MODEL
)