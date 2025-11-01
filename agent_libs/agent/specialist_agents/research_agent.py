"""
Research Agent - Chuyên nghiên cứu mã cổ phiếu về phân tích cơ bản và thị trường
"""
import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from agents import Agent, AgentOutputSchema, WebSearchTool, function_tool
from agent_libs.setting import settings
from agent_libs.tools.stock_market import get_realtime_market_data
from agent_libs.tools.crypto_market import get_crypto_market_data

# Research Agent specializing in comprehensive stock analysis
RESEARCH_PROMPT = (
    "Bạn là một chuyên gia nghiên cứu cổ phiếu với nhiều năm kinh nghiệm trong phân tích đầu tư.\n\n"
    
    "NHIỆM VỤ CỦA BẠN:\n"
    "1. Nhận yêu cầu nghiên cứu cổ phiếu (mã cổ phiếu, tên công ty, hoặc yêu cầu phân tích cụ thể)\n"
    "2. Thu thập thông tin toàn diện về cổ phiếu thông qua các tools trực tiếp\n"
    "3. Phân tích đa chiều: cơ bản, kỹ thuật, thị trường, ngành\n"
    "4. Trả về phân tích chi tiết và có cấu trúc theo format ResearchAnalysis\n\n"
    
    "CÁC TOOLS CÓ SẴN:\n"
    "- get_realtime_market_data: Lấy dữ liệu thị trường chứng khoán Việt Nam và quốc tế (HOSE, HNX, UPCOM)\n"
    "  + Bao gồm: giá hiện tại, volume, market cap, technical indicators (RSI, MACD, MA) nếu bật include_technical_indicators=True\n"
    "- get_crypto_market_data: Lấy dữ liệu thị trường tiền điện tử\n"
    "- web_search: Tìm kiếm thông tin từ web, tin tức, analyst ratings, phân tích ngành\n"
    "- get_time_now: Lấy thời điểm hiện tại để xác định mốc thời gian tìm kiếm\n\n"
    
    "HƯỚNG DẪN SỬ DỤNG TOOLS:\n"
    "Khi nhận yêu cầu phân tích một mã cổ phiếu (ví dụ: VIC, VCB, AAPL):\n"
    "1. XÁC ĐỊNH THỜI ĐIỂM TÌM KIẾM:\n"
    "   - Nếu người dùng KHÔNG nêu rõ thời gian: GỌI get_time_now để lấy thời điểm hiện tại, rồi suy ra mốc thời gian tương ứng (hôm nay/hôm qua/tuần này/tháng này) và CHÈN mốc thời gian vào truy vấn\n"
    "   - Nếu người dùng nêu rõ thời gian (ví dụ: 'hôm nay', 'tuần này', 'tháng này') → dùng đúng mốc thời gian đó\n"
    "2. Thông tin cơ bản và thị trường:\n"
    "   - Gọi get_realtime_market_data với mã cổ phiếu để lấy giá hiện tại, volume, market cap\n"
    "   - Nếu cần technical indicators, đặt include_technical_indicators=True\n"
    "3. Phân tích kỹ thuật:\n"
    "   - Gọi get_realtime_market_data với include_technical_indicators=True để lấy RSI, MACD, Moving Averages\n"
    "4. Tin tức và thị trường:\n"
    "   - Gọi web_search với các query có bao gồm mốc thời gian đã xác định:\n"
    "     + '[mã cổ phiếu] tin tức mới nhất [mốc thời gian]'\n"
    "     + '[mã cổ phiếu] market sentiment [mốc thời gian]'\n"
    "     + '[mã cổ phiếu] analyst ratings'\n"
    "     + '[mã cổ phiếu] P/E ratio P/B ratio ROE'\n"
    "5. Phân tích ngành:\n"
    "   - Gọi web_search với: '[tên ngành] competitors analysis', '[mã cổ phiếu] industry comparison'\n\n"
    
    "CHUYÊN MÔN CỦA BẠN:\n"
    "- **Phân tích cơ bản**: P/E, P/B, ROE, ROA, Debt/Equity, Revenue growth, Profit margins, EPS\n"
    "- **Phân tích kỹ thuật**: RSI, MACD, Moving Averages, Volume trends, Support/Resistance levels\n"
    "- **Phân tích thị trường**: Analyst ratings, Market sentiment, News sentiment, Price targets\n"
    "- **Phân tích ngành**: Industry positioning, Competitive analysis, Market share, Industry trends\n"
    "- **Đánh giá giá trị**: Valuation metrics, Fair value estimation, Growth prospects\n\n"
    
    "QUY TRÌNH XỬ LÝ:\n"
    "1. Xác định mã cổ phiếu/công ty từ yêu cầu\n"
    "2. XÁC ĐỊNH THỜI ĐIỂM: Nếu người dùng không nêu rõ, gọi get_time_now để xác định mốc thời gian mặc định (hôm nay)\n"
    "3. Sử dụng các tools trực tiếp để thu thập:\n"
    "   - Dữ liệu giá và thị trường hiện tại (get_realtime_market_data với include_technical_indicators=True)\n"
    "   - Metrics tài chính cơ bản (từ dữ liệu thị trường và web_search để tìm P/E, P/B, ROE, etc.)\n"
    "   - Chỉ số kỹ thuật (từ get_realtime_market_data với include_technical_indicators=True)\n"
    "   - Tin tức và sentiment (web_search với mốc thời gian đã xác định)\n"
    "   - Thông tin về ngành và đối thủ (web_search)\n"
    "4. Phân tích và đánh giá tổng hợp:\n"
    "   - So sánh với trung bình ngành (từ web_search)\n"
    "   - Đánh giá điểm mạnh/yếu\n"
    "   - Xác định cơ hội và rủi ro\n"
    "5. Tính điểm tổng hợp (0-100) và đưa ra khuyến nghị\n"
    "6. Trả về kết quả chi tiết theo format ResearchAnalysis\n\n"
    
    "QUAN TRỌNG:\n"
    "- Cung cấp phân tích chính xác, khách quan và có căn cứ rõ ràng\n"
    "- Sử dụng dữ liệu thực từ các tools, tránh gọi lại tool trùng lặp\n"
    "- LUÔN ưu tiên dữ liệu theo đúng mốc thời gian người dùng yêu cầu; nếu người dùng không nêu rõ, mặc định là 'hôm nay'\n"
    "- Với tìm kiếm web, thêm bộ lọc/ngữ cảnh thời gian phù hợp (ví dụ: today, past 24h, ngày YYYY-MM-DD)\n"
    "- Trong phần summary, nêu rõ khung thời gian dữ liệu (ví dụ: 'Dữ liệu ngày YYYY-MM-DD')\n"
    "- Đưa ra khuyến nghị đầu tư (Buy/Hold/Sell) dựa trên phân tích toàn diện\n"
    "- Phân tích phải bao gồm đầy đủ: cơ bản, kỹ thuật, thị trường và ngành\n"
    "- Tránh lặp lại các phân tích không cần thiết\n"
    "- Đảm bảo tất cả metrics và insights đều có nguồn dữ liệu rõ ràng từ tools"
)


class FundamentalMetrics(BaseModel):
    """Các chỉ số tài chính cơ bản"""
    pe_ratio: Optional[float] = Field(default=None, description="P/E ratio")
    pb_ratio: Optional[float] = Field(default=None, description="P/B ratio")
    roe: Optional[float] = Field(default=None, description="ROE (%)")
    roa: Optional[float] = Field(default=None, description="ROA (%)")
    debt_to_equity: Optional[float] = Field(default=None, description="Debt/Equity ratio")
    revenue_growth: Optional[float] = Field(default=None, description="Revenue growth (%)")
    profit_margin: Optional[float] = Field(default=None, description="Profit margin (%)")
    eps: Optional[float] = Field(default=None, description="Earnings per share")
    

class TechnicalIndicators(BaseModel):
    """Chỉ số phân tích kỹ thuật"""
    rsi: Optional[float] = Field(default=None, description="RSI (14)")
    macd: Optional[Dict[str, Any]] = Field(default_factory=dict, description="MACD indicator")
    moving_averages: Optional[Dict[str, float]] = Field(default_factory=dict, description="MA 20, 50, 200")
    volume_trend: Optional[str] = Field(default=None, description="Volume trend analysis")
    support_level: Optional[float] = Field(default=None, description="Support price level")
    resistance_level: Optional[float] = Field(default=None, description="Resistance price level")
    trend: Optional[str] = Field(default=None, description="Price trend: bullish/bearish/neutral")
    

class MarketSentiment(BaseModel):
    """Tâm lý thị trường"""
    analyst_rating: Optional[str] = Field(default=None, description="Overall analyst rating")
    price_target: Optional[float] = Field(default=None, description="Average price target")
    sentiment: Optional[str] = Field(default=None, description="Market sentiment: positive/neutral/negative")
    news_sentiment: Optional[str] = Field(default=None, description="News sentiment")
    

class ResearchAnalysis(BaseModel):
    """Kết quả phân tích nghiên cứu cổ phiếu toàn diện"""
    symbol: str
    """Mã cổ phiếu được phân tích"""
    company_name: Optional[str] = Field(default=None, description="Tên công ty")
    current_price: Optional[float] = Field(default=None, description="Giá hiện tại")
    market_cap: Optional[float] = Field(default=None, description="Vốn hóa thị trường")
    analysis_summary: str
    """Tóm tắt phân tích toàn diện"""
    recommendation: str
    """Khuyến nghị đầu tư: Buy/Hold/Sell"""
    score: int = Field(ge=0, le=100, description="Điểm tổng hợp (0-100, cao hơn = tốt hơn)")
    fundamental_metrics: Optional[FundamentalMetrics] = Field(default=None, description="Metrics tài chính cơ bản")
    technical_indicators: Optional[TechnicalIndicators] = Field(default=None, description="Chỉ số kỹ thuật")
    market_sentiment: Optional[MarketSentiment] = Field(default=None, description="Tâm lý thị trường")
    key_metrics: Dict[str, Any] = Field(default_factory=dict, description="Các metrics quan trọng khác")
    risk_factors: List[str] = Field(default_factory=list, description="Các yếu tố rủi ro")
    opportunities: List[str] = Field(default_factory=list, description="Các cơ hội đầu tư")
    key_insights: List[str] = Field(default_factory=list, description="Các insights quan trọng")
    industry_comparison: Optional[Dict[str, Any]] = Field(default_factory=dict, description="So sánh với ngành")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Độ tin cậy phân tích (0-1)")
    
    pass


@function_tool
async def get_time_now() -> str:
    """Get current time in ISO format"""
    return "Time now is " + datetime.datetime.now().isoformat()


research_agent = Agent(
    name="ResearchAgent",
    instructions=RESEARCH_PROMPT,
    output_type=AgentOutputSchema(ResearchAnalysis, strict_json_schema=False),
    tools=[
        get_realtime_market_data,
        get_crypto_market_data,
        WebSearchTool(),
        get_time_now
    ],
    model=settings.OPENAI_MODEL
)
