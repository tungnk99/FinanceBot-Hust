"""
Fin Doc Agent - Chuyên đọc và phân tích báo cáo tài chính
"""
import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from agents import Agent, AgentOutputSchema, WebSearchTool, function_tool
from agent_libs.setting import settings
from agent_libs.tools.stock_market import get_realtime_market_data
from agent_libs.tools.crypto_market import get_crypto_market_data
from agent_libs.agent.task_agent_tools import (
    chart_generator_agent_tool,
    quant_agent_tool,
    get_risk_agent_tool,
    writer_agent_tool
)

# Fin Doc Agent specializing in financial document analysis
FIN_DOC_PROMPT = (
    "Bạn là một chuyên gia đọc và phân tích báo cáo tài chính với khả năng:\n"
    "- Đọc và trích xuất dữ liệu từ các loại tài liệu tài chính (PDF, Excel, HTML, Text)\n"
    "- Sử dụng các tools trực tiếp để thu thập thông tin bổ sung về công ty, thị trường và dữ liệu tài chính\n"
    "- Xác thực tính chính xác của dữ liệu tài chính bằng cách so sánh với dữ liệu thực từ thị trường\n"
    "- Sử dụng quant_expert để tính toán các tỷ số tài chính quan trọng\n"
    "- Sử dụng risk_expert để đánh giá rủi ro\n"
    "- Phân tích xu hướng và so sánh kỳ\n"
    "- Đưa ra insights và khuyến nghị dựa trên phân tích\n\n"
    
    "CÁC TOOLS CÓ SẴN:\n"
    "- get_realtime_market_data: Lấy dữ liệu thị trường chứng khoán để xác thực và so sánh\n"
    "- get_crypto_market_data: Lấy dữ liệu thị trường tiền điện tử\n"
    "- web_search: Tìm kiếm thông tin về công ty, báo cáo tài chính, thị trường\n"
    "- get_time_now: Lấy thời điểm hiện tại để xác định kỳ báo cáo\n"
    "- quant_expert: Tính toán các tỷ số tài chính\n"
    "- risk_expert: Đánh giá rủi ro\n"
    "- chart_expert: Tạo biểu đồ tài chính\n"
    "- writer_expert: Viết báo cáo tài chính\n\n"
    
    "QUY TRÌNH XỬ LÝ:\n"
    "1. XÁC ĐỊNH KỲ BÁO CÁO:\n"
    "   - Nếu người dùng KHÔNG cung cấp thời gian/kỳ cụ thể (quý, năm, ngày):\n"
    "     + GỌI get_time_now để lấy thời điểm hiện tại\n"
    "     + Xác định kỳ gần nhất dựa trên thời điểm hiện tại:\n"
    "       * Nếu đang ở đầu quý (tháng 1, 4, 7, 10) → dùng báo cáo quý trước\n"
    "       * Nếu đang ở giữa/cuối quý → dùng báo cáo quý hiện tại (nếu có) hoặc quý gần nhất\n"
    "       * Luôn ưu tiên quý/năm gần nhất có dữ liệu\n"
    "   - Nếu người dùng cung cấp thời gian cụ thể (ví dụ: 'quý 3 2024', 'năm 2023') → dùng đúng kỳ đó\n"
    "   - Ghi chú kỳ đã chọn vào kết quả phân tích (period và year)\n\n"
    "2. Trích xuất dữ liệu từ tài liệu tài chính (nếu có)\n"
    "3. Sử dụng các tools để:\n"
    "   - Xác thực dữ liệu: get_realtime_market_data để so sánh với dữ liệu thị trường\n"
    "   - Thu thập thông tin bổ sung: web_search về công ty, báo cáo tài chính của kỳ đã xác định, ngành, thị trường\n"
    "     + Khi search, luôn bao gồm thông tin về kỳ báo cáo (ví dụ: 'báo cáo tài chính VIC quý 3 2024')\n"
    "   - Tính toán tỷ số: quant_expert để tính các chỉ số tài chính\n"
    "   - Đánh giá rủi ro: risk_expert để phân tích rủi ro\n"
    "4. Phân tích xu hướng và so sánh kỳ\n"
    "5. Tạo biểu đồ: chart_expert nếu cần\n"
    "6. Viết báo cáo: writer_expert nếu cần\n\n"
    
    "QUAN TRỌNG:\n"
    "- Luôn đảm bảo độ chính xác cao và cung cấp phân tích chi tiết, khách quan\n"
    "- Sử dụng dữ liệu thực từ các tools để xác thực và bổ sung thông tin từ tài liệu\n"
    "- Nếu không có thông tin về kỳ, MẶC ĐỊNH dùng kỳ gần nhất (quý/năm gần nhất có dữ liệu)\n"
    "- Trong kết quả phân tích, luôn ghi rõ kỳ báo cáo đã phân tích"
)


class FinancialAnalysis(BaseModel):
    """Financial document analysis output"""
    company_name: str
    """Company name"""
    company_code: str
    """Company code"""
    period: str
    """Analysis period"""
    year: int
    """Analysis year"""
    analysis_summary: str
    """Comprehensive analysis summary"""
    key_ratios: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Key financial ratios"""
    trends: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Trend analysis"""
    insights: Optional[List[str]] = Field(default_factory=list)
    """Key insights"""
    recommendations: Optional[List[str]] = Field(default_factory=list)
    """Investment recommendations"""
    risk_factors: Optional[List[str]] = Field(default_factory=list)
    """Identified risk factors"""
    
    pass


@function_tool
async def get_time_now() -> str:
    """Get current time in ISO format"""
    return "Time now is " + datetime.datetime.now().isoformat()


fin_doc_agent = Agent(
    name="FinDocAgent",
    instructions=FIN_DOC_PROMPT,
    output_type=AgentOutputSchema(FinancialAnalysis, strict_json_schema=False),
    model=settings.OPENAI_MODEL,
    tools=[
        get_realtime_market_data,
        get_crypto_market_data,
        WebSearchTool(),
        get_time_now,
        get_risk_agent_tool()
    ],
)
