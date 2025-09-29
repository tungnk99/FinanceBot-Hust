"""
Quantitative Analysis Agent - Chuyên phân tích định lượng tài chính
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum

from agents import Agent, AgentOutputSchema
from src.tools.yfinance_data import get_stock_data, get_crypto_data, get_market_data_for_technical_analysis, get_stock_with_technical_analysis
from src.tools.technical_analysis import perform_technical_analysis, calculate_risk_metrics
from src.setting import settings


class AnalysisType(str, Enum):
    """Types of quantitative analysis"""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    RISK = "risk"
    VALUATION = "valuation"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    CORRELATION = "correlation"
    REGRESSION = "regression"
    PORTFOLIO = "portfolio"


# Quantitative Analysis Agent specializing in financial data analysis
QUANT_PROMPT = (
    "Bạn là một chuyên gia phân tích định lượng tài chính.\n\n"
    
    "NHIỆM VỤ CỦA BẠN:\n"
    "1. Nhận yêu cầu phân tích định lượng\n"
    "2. Sử dụng tools để lấy dữ liệu thị trường thực tế\n"
    "3. Phân tích và tính toán các metrics cần thiết\n"
    "4. Trả về kết quả phân tích có cấu trúc\n\n"
    
    "CHUYÊN MÔN CỦA BẠN:\n"
    "- Phân tích kỹ thuật: RSI, MACD, Moving Averages, Bollinger Bands\n"
    "- Phân tích cơ bản: P/E, P/B, ROE, ROA, Debt ratios\n"
    "- Phân tích rủi ro: VaR, Beta, Volatility analysis\n"
    "- Định giá: DCF, P/E multiples, Comparable analysis\n\n"
    
    "QUY TRÌNH XỬ LÝ:\n"
    "1. Phân tích yêu cầu để xác định loại phân tích cần thiết\n"
    "2. Sử dụng get_stock_with_technical_analysis để lấy dữ liệu + tính indicators trong 1 bước (KHUYẾN NGHỊ)\n"
    "3. Hoặc sử dụng get_stock_data + perform_technical_analysis (2 bước riêng biệt)\n"
    "4. Sử dụng calculate_risk_metrics để tính volatility, Sharpe ratio, VaR\n"
    "5. Trả về kết quả theo format QuantitativeAnalysis\n\n"
    
    "QUAN TRỌNG:\n"
    "- KHUYẾN NGHỊ: Sử dụng get_stock_with_technical_analysis để có cả dữ liệu và indicators trong 1 lần gọi\n"
    "- Tool này tự động lấy dữ liệu từ yfinance và tính RSI, MACD, Moving Averages, Bollinger Bands\n"
    "- Nếu cần chi tiết hơn, có thể dùng get_stock_data + perform_technical_analysis riêng biệt\n"
    "- Sử dụng calculate_risk_metrics để tính các metrics rủi ro\n"
    "- Nếu không có dữ liệu, trả về empty dict/list thay vì None\n"
    "- Tránh lặp lại các tính toán không cần thiết"
)


class QuantitativeAnalysis(BaseModel):
    """Quantitative analysis output"""
    symbol: str
    """Asset symbol analyzed"""
    analysis_type: AnalysisType
    """Type of analysis performed"""
    metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Quantitative metrics calculated"""
    indicators: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Technical indicators"""
    signals: Optional[List[str]] = Field(default_factory=list)
    """Trading signals"""
    risk_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Risk assessment metrics"""
    valuation: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """Valuation analysis"""
    recommendations: Optional[List[str]] = Field(default_factory=list)    
    """Investment recommendations"""
    confidence_score: Optional[float] = Field(default=0.0)
    """Confidence score (0-1)"""
    
    pass


quant_agent = Agent(
    name="QuantitativeAnalysisAgent",
    instructions=QUANT_PROMPT,
    output_type=AgentOutputSchema(QuantitativeAnalysis, strict_json_schema=False),
    tools=[
        get_stock_data,
        get_crypto_data,
        get_market_data_for_technical_analysis,
        get_stock_with_technical_analysis,  # Tool mới: lấy dữ liệu + tính indicators trong 1 bước
        perform_technical_analysis,
        calculate_risk_metrics
    ],
    model=settings.OPENAI_MODEL
)
