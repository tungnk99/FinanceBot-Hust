"""
Request schemas for FinanceBot API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
# Removed dependency on agent_libs.agents which is not available at runtime


class HistoryMessage(BaseModel):
    """History message model"""
    role: str = Field(..., description="Message role (user/assistant)")
    message: str = Field(..., description="Message content")
    created_at: Optional[str] = Field(default="", description="Timestamp in ISO format")


class AttachFile(BaseModel):
    """Attached file model"""
    url: str = Field(..., description="File URL")
    filename: Optional[str] = Field(default="", description="File name")
    mime_type: Optional[str] = Field(default="", description="MIME type")
    sha256: Optional[str] = Field(default="", description="SHA256 hash")
    
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "url": "https://example.com/file.pdf",
                "filename": "file.pdf",
                "mime_type": "application/pdf",
                "sha256": "1234567890"
            }
        }


class ChatContext(BaseModel):
    """Context model for chat requests"""
    history: Optional[List[HistoryMessage]] = Field(default=None, description="Chat history")
    deep_research: Optional[bool] = Field(default=False, description="Enable deep research mode")
    attach_files: Optional[List[AttachFile]] = Field(default=None, description="List of attached files as JSON objects")

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "history": [
                    {"role": "user", "message": "What is the current price of AAPL?", "created_at": datetime.now().isoformat()},
                    {"role": "assistant", "message": "The current price of AAPL is $150.00", "created_at": datetime.now().isoformat()}
                ],
                "deep_research": True,
                "attach_files": [{"url": "https://example.com/file.pdf", "filename": "file.pdf", "mime_type": "application/pdf", "sha256": "1234567890"}]
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message/query", min_length=1)
    session_id: Optional[str] = Field(default="string", description="Session ID")
    user_id: Optional[str] = Field(default="string", description="User ID")
    context: Optional[ChatContext] = Field(default=None, description="Additional context for the chat request")


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
