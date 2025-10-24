"""
Request schemas for FinanceBot API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from src.agents.planner_agents.master_agent import QueryType, Priority


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message/query", min_length=1)
    session_id: Optional[str] = Field(default=None, description="Session ID")
    user_id: Optional[str] = Field(default=None, description="User ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class StockAnalysisRequest(BaseModel):
    """Request model for stock analysis"""
    symbol: str = Field(..., description="Stock symbol (e.g., VIC, AAPL)", min_length=1, max_length=10)
    analysis_type: str = Field(
        default="comprehensive", 
        description="Type of analysis",
        pattern="^(comprehensive|technical|fundamental|quick)$"
    )
    timeframe: Optional[str] = Field(
        default="1 year", 
        description="Analysis timeframe",
        pattern="^(1 month|3 months|6 months|1 year|2 years|5 years)$"
    )
    indicators: Optional[List[str]] = Field(
        default=None, 
        description="Technical indicators",
        max_items=10
    )


class ChartRequest(BaseModel):
    """Request model for chart generation"""
    symbol: str = Field(..., description="Stock symbol", min_length=1, max_length=10)
    chart_type: str = Field(
        default="price with moving averages", 
        description="Type of chart",
        min_length=5
    )
    timeframe: Optional[str] = Field(
        default="1 year", 
        description="Chart timeframe",
        pattern="^(1 month|3 months|6 months|1 year|2 years|5 years)$"
    )


class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment"""
    symbol: str = Field(..., description="Stock symbol", min_length=1, max_length=10)
    risk_factors: Optional[List[str]] = Field(
        default=None,
        description="Specific risk factors to assess",
        max_items=10
    )
    timeframe: Optional[str] = Field(
        default="1 year",
        description="Risk assessment timeframe",
        pattern="^(1 month|3 months|6 months|1 year|2 years|5 years)$"
    )


class ReportRequest(BaseModel):
    """Request model for report generation"""
    symbol: str = Field(..., description="Stock symbol", min_length=1, max_length=10)
    report_type: str = Field(
        default="investment analysis",
        description="Type of report",
        pattern="^(investment analysis|earnings report|market outlook|risk report)$"
    )
    sections: Optional[List[str]] = Field(
        default=None,
        description="Specific sections to include",
        max_items=10
    )
    target_audience: Optional[str] = Field(
        default="general",
        description="Target audience",
        pattern="^(general|professional|beginner|expert)$"
    )
