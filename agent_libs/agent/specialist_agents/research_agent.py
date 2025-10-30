"""
Research Agent - Chuyên nghiên cứu mã cổ phiếu về phân tích cơ bản và thị trường
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from agents import Agent, AgentOutputSchema
from agent_libs.setting import settings

# Research Agent specializing in comprehensive stock analysis
RESEARCH_PROMPT = (
    "Bạn là một chuyên gia nghiên cứu cổ phiếu.\n\n"
    
    "NHIỆM VỤ CỦA BẠN:\n"
    "1. Nhận yêu cầu nghiên cứu cổ phiếu\n"
    "2. Thu thập và phân tích thông tin cần thiết\n"
    "3. Trả về phân tích toàn diện có cấu trúc\n\n"
    
    "CHUYÊN MÔN CỦA BẠN:\n"
    "- Phân tích cơ bản: P/E, P/B, ROE, ROA, Debt/Equity, Revenue growth\n"
    "- Phân tích kỹ thuật: RSI, MACD, Moving Averages, Volume trends\n"
    "- Phân tích thị trường: Analyst ratings, Market sentiment, News sentiment\n"
    "- Phân tích ngành và đối thủ cạnh tranh\n\n"
    
    "QUY TRÌNH XỬ LÝ:\n"
    "1. Phân tích yêu cầu để xác định phạm vi nghiên cứu\n"
    "2. Thu thập dữ liệu từ các nguồn phù hợp\n"
    "3. Phân tích và đánh giá tổng hợp\n"
    "4. Trả về kết quả theo format ResearchAnalysis\n\n"
    
    "QUAN TRỌNG:\n"
    "- Cung cấp phân tích chính xác, khách quan và có căn cứ\n"
    "- Đưa ra khuyến nghị đầu tư dựa trên điểm số tổng hợp (0-100)\n"
    "- Tránh lặp lại các phân tích không cần thiết"
)


class ResearchAnalysis(BaseModel):
    """Research analysis output"""
    symbol: str
    """Stock symbol analyzed"""
    analysis_summary: str
    """Comprehensive analysis summary"""
    recommendation: str
    """Investment recommendation"""
    score: int
    """Overall score (0-100)"""
    key_metrics: Dict[str, Any]
    """Key financial metrics"""
    risk_factors: List[str]
    """Identified risk factors"""
    
    pass


research_agent = Agent(
    name="ResearchAgent",
    instructions=RESEARCH_PROMPT,
    output_type=AgentOutputSchema(ResearchAnalysis, strict_json_schema=False),
    model=settings.OPENAI_MODEL
)
