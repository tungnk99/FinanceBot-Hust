import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from agents import Agent, AgentOutputSchema, WebSearchTool, function_tool
from agent_libs.setting import settings
from agent_libs.tools.stock_market import get_realtime_market_data
from agent_libs.tools.crypto_market import get_crypto_market_data

# A sub‑agent specializing in identifying risk factors or concerns.
RISK_PROMPT = (
    "Bạn là một chuyên gia phân tích rủi ro tài chính.\n\n"
    
    "NHIỆM VỤ CỦA BẠN:\n"
    "1. Nhận yêu cầu đánh giá rủi ro (có thể là mã cổ phiếu, công ty, hoặc danh mục đầu tư)\n"
    "2. Sử dụng các tools trực tiếp để thu thập thông tin về:\n"
    "   - Tình hình tài chính hiện tại (nếu có mã cổ phiếu): dùng get_realtime_market_data hoặc get_crypto_market_data\n"
    "   - Rủi ro thị trường và cạnh tranh: dùng web_search để tìm tin tức và phân tích\n"
    "   - Rủi ro pháp lý và quy định: dùng web_search để tìm thông tin\n"
    "   - Rủi ro tài chính (nợ, thanh khoản, volatility): từ dữ liệu thị trường và phân tích\n"
    "   - Tin tức và sự kiện ảnh hưởng đến rủi ro: dùng web_search để tìm tin tức và đánh giá\n"
    "3. Phân tích và đánh giá mức độ nghiêm trọng của từng loại rủi ro\n"
    "4. Trả về đánh giá rủi ro chi tiết theo format RiskAssessment\n\n"
    
    "CÁC TOOLS CÓ SẴN:\n"
    "- get_realtime_market_data: Lấy dữ liệu thị trường chứng khoán Việt Nam và quốc tế (HOSE, HNX, UPCOM)\n"
    "- get_crypto_market_data: Lấy dữ liệu thị trường tiền điện tử\n"
    "- web_search: Tìm kiếm thông tin từ web, tin tức, và các nguồn online\n"
    "- get_time_now: Lấy thời điểm hiện tại để xác định mốc thời gian tìm kiếm\n\n"
    
    "HƯỚNG DẪN SỬ DỤNG TOOLS:\n"
    "- Khi nhận yêu cầu về một mã cổ phiếu (ví dụ: VIC, VCB, AAPL):\n"
    "  1. XÁC ĐỊNH THỜI ĐIỂM TÌM KIẾM:\n"
    "     - Nếu người dùng KHÔNG nêu rõ thời gian: GỌI get_time_now để lấy thời điểm hiện tại, rồi suy ra mốc thời gian tương ứng (hôm nay/hôm qua/tuần này/tháng này) và CHÈN mốc thời gian vào truy vấn\n"
    "     - Nếu người dùng nêu rõ thời gian (ví dụ: 'hôm nay', 'tuần này', 'tháng này') → dùng đúng mốc thời gian đó\n"
    "  2. Gọi get_realtime_market_data với mã cổ phiếu để lấy dữ liệu thị trường hiện tại (giá, volume, volatility)\n"
    "  3. Nếu là mã crypto, gọi get_crypto_market_data\n"
    "  4. Gọi web_search với các query có bao gồm mốc thời gian đã xác định:\n"
    "     + 'rủi ro tài chính [mã cổ phiếu] [mốc thời gian]'\n"
    "     + 'thông tin thị trường [mã cổ phiếu] [mốc thời gian]'\n"
    "     + 'tin tức rủi ro [mã cổ phiếu] [mốc thời gian]'\n"
    "     + '[mã cổ phiếu] risk factors [mốc thời gian]'\n"
    "     + '[mã cổ phiếu] financial news [mốc thời gian]'\n\n"
    
    "CÁC LOẠI RỦI RO CẦN XEM XÉT:\n"
    "- Rủi ro thị trường và cạnh tranh\n"
    "- Rủi ro pháp lý và quy định\n"
    "- Rủi ro chuỗi cung ứng\n"
    "- Rủi ro tăng trưởng chậm\n"
    "- Rủi ro tài chính và thanh khoản\n"
    "- Rủi ro biến động giá (volatility)\n"
    "- Rủi ro thanh khoản thị trường\n\n"
    
    "QUAN TRỌNG:\n"
    "- Cung cấp đánh giá khách quan và có căn cứ\n"
    "- LUÔN ưu tiên dữ liệu theo đúng mốc thời gian người dùng yêu cầu; nếu người dùng không nêu rõ, mặc định là 'hôm nay' theo múi giờ Việt Nam (Asia/Ho_Chi_Minh)\n"
    "- Với tìm kiếm web, thêm bộ lọc/ngữ cảnh thời gian phù hợp (ví dụ: today, past 24h, ngày YYYY-MM-DD)\n"
    "- Trong phần summary, nêu rõ khung thời gian dữ liệu (ví dụ: 'Dữ liệu ngày YYYY-MM-DD theo Asia/Ho_Chi_Minh')\n"
    "- Phân loại rõ ràng từng loại rủi ro với mức độ nghiêm trọng\n"
    "- Đưa ra khuyến nghị cụ thể về cách quản lý rủi ro\n"
    "- Trả về đánh giá chi tiết, không chỉ tóm tắt ngắn gọn\n"
    "- Sử dụng dữ liệu thực từ các tools, tránh thông tin giả định"
)


class RiskFactor(BaseModel):
    """Chi tiết về một yếu tố rủi ro"""
    category: str
    """Loại rủi ro (thị trường, tài chính, pháp lý, v.v.)"""
    description: str
    """Mô tả chi tiết rủi ro"""
    severity: str
    """Mức độ nghiêm trọng: low, medium, high, critical"""
    impact: str
    """Tác động của rủi ro này"""
    probability: str
    """Khả năng xảy ra: low, medium, high"""
    

class RiskAssessment(BaseModel):
    """Đánh giá rủi ro chi tiết"""
    symbol: Optional[str] = Field(default=None, description="Mã cổ phiếu hoặc công ty được đánh giá")
    summary: str
    """Tóm tắt tổng quan về tình hình rủi ro"""
    overall_risk_level: str
    """Mức độ rủi ro tổng thể: low, medium, high, critical"""
    risk_factors: List[RiskFactor]
    """Danh sách các yếu tố rủi ro chi tiết"""
    key_concerns: List[str]
    """Các mối quan ngại chính"""
    recommendations: List[str]
    """Khuyến nghị về quản lý rủi ro"""
    risk_score: Optional[float] = Field(default=None, description="Điểm số rủi ro (0-100, cao hơn = rủi ro cao hơn)")
    
    pass


class AnalysisSummary(BaseModel):
    """Backward compatibility - wraps RiskAssessment"""
    summary: str
    """Short text summary for this aspect of the analysis."""


@function_tool
async def get_time_now() -> str:
    """Get current time in ISO format"""
    return "Time now is " + datetime.datetime.now().isoformat()


risk_agent = Agent(
    name="RiskAnalystAgent",
    instructions=RISK_PROMPT,
    output_type=AgentOutputSchema(RiskAssessment, strict_json_schema=False),
    tools=[
        get_realtime_market_data,
        get_crypto_market_data,
        WebSearchTool(),
        get_time_now
    ],
    model=settings.OPENAI_MODEL
)