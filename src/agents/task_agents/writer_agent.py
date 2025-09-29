from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

from agents import Agent, AgentOutputSchema
from src.setting import settings


class InvestmentRating(str, Enum):
    """Investment rating scale"""
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"


class RiskLevel(str, Enum):
    """Risk level classification"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class MarketOutlook(str, Enum):
    """Market outlook classification"""
    VERY_BULLISH = "Very Bullish"
    BULLISH = "Bullish"
    NEUTRAL = "Neutral"
    BEARISH = "Bearish"
    VERY_BEARISH = "Very Bearish"


class FinancialAnalysisSection(BaseModel):
    """Individual section of financial analysis"""
    title: str
    """Section title"""
    content: str
    """Section content in markdown format"""
    key_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Key metrics for this section"""
    charts_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Data for charts/visualizations"""


class InvestmentRecommendation(BaseModel):
    """Investment recommendation details"""
    rating: InvestmentRating
    """Investment rating"""
    target_price: Optional[float] = Field(default=None)
    """Target price if applicable"""
    time_horizon: str
    """Investment time horizon (e.g., '6-12 months', 'Long-term')"""
    confidence_level: float
    """Confidence level (0.0 to 1.0)"""
    rationale: str
    """Reasoning behind the recommendation"""


class RiskAssessment(BaseModel):
    """Risk assessment details"""
    overall_risk: RiskLevel
    """Overall risk level"""
    key_risks: Optional[List[str]] = Field(default_factory=list)
    """List of key risk factors"""
    risk_mitigation: Optional[str] = Field(default=None)
    """Risk mitigation strategies"""
    volatility_assessment: Optional[str] = Field(default=None)
    """Volatility assessment"""


class MarketContext(BaseModel):
    """Market context and outlook"""
    sector_outlook: MarketOutlook
    """Sector outlook"""
    market_conditions: str
    """Current market conditions description"""
    macroeconomic_factors: Optional[List[str]] = Field(default_factory=list)
    """Relevant macroeconomic factors"""
    competitive_landscape: Optional[str] = Field(default=None)
    """Competitive landscape analysis"""


class ProfessionalFinancialReport(BaseModel):
    """Comprehensive professional financial analysis report"""
    
    # Executive Summary
    executive_summary: str
    """Executive summary (2-3 paragraphs)"""
    
    # Investment Recommendation
    recommendation: InvestmentRecommendation
    """Investment recommendation and rating"""
    
    # Risk Assessment
    risk_assessment: RiskAssessment
    """Comprehensive risk assessment"""
    
    # Market Context
    market_context: MarketContext
    """Market and sector context"""
    
    # Analysis Sections
    analysis_sections: Optional[List[FinancialAnalysisSection]] = Field(default_factory=list)
    """Detailed analysis sections including:
    - Company Overview
    - Financial Performance Analysis
    - Fundamental Analysis
    - Technical Analysis
    - Competitive Analysis
    - Growth Prospects
    - Valuation Analysis
    """
    
    # Key Metrics Summary
    key_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Summary of key financial metrics"""
    
    # Charts and Visualizations
    charts_summary: Optional[str] = Field(default=None)
    """Summary of charts and visualizations included"""
    
    # Full Report
    full_report: str
    """Complete markdown report with all sections"""
    
    # Follow-up Research
    follow_up_questions: Optional[List[str]] = Field(default_factory=list)
    """Suggested follow-up research questions"""
    
    # Data Sources
    data_sources: Optional[List[str]] = Field(default_factory=list)
    """Sources of data and information used"""
    
    # Disclaimer
    disclaimer: str
    """Standard financial analysis disclaimer"""
    
    pass


# Enhanced writer agent with professional financial report capabilities
WRITER_PROMPT = """
Bạn là một chuyên gia phân tích tài chính cấp cao với 15+ năm kinh nghiệm.

NHIỆM VỤ CỦA BẠN:
1. Nhận yêu cầu viết báo cáo phân tích tài chính
2. Thu thập thông tin từ các nguồn cần thiết
3. Tổng hợp và viết báo cáo chuyên nghiệp

CẤU TRÚC BÁO CÁO:
1. Executive Summary (2-3 đoạn)
2. Investment Recommendation (rating, target price, time horizon)
3. Risk Assessment (đánh giá rủi ro toàn diện)
4. Market Context (bối cảnh thị trường)
5. Detailed Analysis Sections (phân tích chi tiết)

QUY TRÌNH XỬ LÝ:
1. Phân tích yêu cầu để xác định phạm vi báo cáo
2. Gọi specialist agents DUY NHẤT MỘT LẦN nếu cần:
   - quant_agent: cho phân tích kỹ thuật
   - risk_agent: cho đánh giá rủi ro
   - research_agent: cho nghiên cứu thị trường
   - fin_doc_agent: cho phân tích tài liệu
3. Tổng hợp thông tin và viết báo cáo hoàn chỉnh
4. Trả về báo cáo theo format ProfessionalFinancialReport

QUAN TRỌNG:
- KHÔNG gọi lại cùng một agent với cùng yêu cầu
- Sử dụng tone chuyên nghiệp phù hợp với báo cáo đầu tư
- Hỗ trợ tất cả claims bằng dữ liệu và evidence
- Cung cấp insights rõ ràng và actionable
- Duy trì tính khách quan và cân bằng
"""


# Professional financial writer agent
writer_agent = Agent(
    name="ProfessionalFinancialWriterAgent",
    instructions=WRITER_PROMPT,
    model=settings.OPENAI_MODEL,
    output_type=AgentOutputSchema(ProfessionalFinancialReport, strict_json_schema=False),
)