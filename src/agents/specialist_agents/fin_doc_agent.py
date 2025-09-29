"""
Fin Doc Agent - Chuyên đọc và phân tích báo cáo tài chính
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from agents import Agent, AgentOutputSchema
from agents.model_settings import ModelSettings
from ...tools.retrieval_tool import retrieval_tool
from ...tools.stock_market import get_realtime_market_data
from ..task_agent_tools import (
    chart_generator_agent_tool,
    quant_agent_tool,
    get_risk_agent_tool,
    writer_agent_tool
)
from src.setting import settings

# Fin Doc Agent specializing in financial document analysis
FIN_DOC_PROMPT = (
    "Bạn là một chuyên gia đọc và phân tích báo cáo tài chính với khả năng:\n"
    "- Đọc và trích xuất dữ liệu từ các loại tài liệu tài chính (PDF, Excel, HTML, Text)\n"
    "- Xác thực tính chính xác của dữ liệu tài chính\n"
    "- Tính toán các tỷ số tài chính quan trọng\n"
    "- Phân tích xu hướng và so sánh kỳ\n"
    "- Đưa ra insights và khuyến nghị dựa trên phân tích\n\n"
    "Luôn đảm bảo độ chính xác cao và cung cấp phân tích chi tiết, khách quan."
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


fin_doc_agent = Agent(
    name="FinDocAgent",
    instructions=FIN_DOC_PROMPT,
    output_type=AgentOutputSchema(FinancialAnalysis, strict_json_schema=False),
    model=settings.OPENAI_MODEL,
    tools=[
        quant_agent_tool,
        get_risk_agent_tool(),
        writer_agent_tool
    ],
    model_settings=ModelSettings(tool_choice="auto"),
)
