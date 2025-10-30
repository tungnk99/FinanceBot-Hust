"""
Professional Chart Generator Agent for Financial Analysis
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from agents import Agent, AgentOutputSchema, CodeInterpreterTool
from agent_libs.setting import settings


class ChartType(str, Enum):
    """Types of financial charts supported"""
    LINE_CHART = "line_chart"
    CANDLESTICK = "candlestick"
    OHLC = "ohlc"
    AREA_CHART = "area_chart"
    MOVING_AVERAGES = "moving_averages"
    BOLLINGER_BANDS = "bollinger_bands"
    RSI = "rsi"
    MACD = "macd"
    VOLUME = "volume"
    REVENUE_CHART = "revenue_chart"
    PROFIT_MARGIN = "profit_margin"
    DEBT_RATIO = "debt_ratio"
    PE_RATIO = "pe_ratio"
    ROE_ROA = "roe_roa"
    COMPARISON_CHART = "comparison_chart"
    CORRELATION_MATRIX = "correlation_matrix"
    SECTOR_COMPARISON = "sector_comparison"


# Chart Generator Agent specializing in financial visualizations
CHART_PROMPT = (
    "Bạn là một chuyên gia tạo biểu đồ tài chính chuyên nghiệp.\n\n"
    
    "NHIỆM VỤ CỦA BẠN:\n"
    "1. Nhận yêu cầu tạo biểu đồ tài chính\n"
    "2. Sử dụng CodeInterpreterTool để viết Python code\n"
    "3. Tạo biểu đồ bằng matplotlib và lưu thành file PNG\n"
    "4. Trả về thông tin biểu đồ đã tạo\n\n"
    
    "CHUYÊN MÔN CỦA BẠN:\n"
    "- Tạo các loại biểu đồ tài chính: line chart, candlestick, OHLC, area chart\n"
    "- Biểu đồ phân tích kỹ thuật: moving averages, Bollinger Bands, RSI, MACD, volume\n"
    "- Biểu đồ phân tích tài chính: revenue, profit margin, debt ratio, P/E ratio, ROE/ROA\n"
    "- Biểu đồ so sánh: comparison chart, correlation matrix, sector comparison\n\n"
    
    "QUY TRÌNH XỬ LÝ:\n"
    "1. Phân tích yêu cầu để xác định loại biểu đồ cần tạo\n"
    "2. Sử dụng CodeInterpreterTool để viết Python code với matplotlib\n"
    "3. Code phải lưu biểu đồ thành file PNG với tên mô tả\n"
    "4. Trả về thông tin biểu đồ theo format GeneratedChart\n\n"
    
    "QUAN TRỌNG:\n"
    "- Luôn sử dụng CodeInterpreterTool để tạo code Python\n"
    "- Code phải sử dụng matplotlib, pandas, numpy\n"
    "- Lưu biểu đồ thành file PNG với plt.savefig()\n"
    "- Biểu đồ phải chuyên nghiệp, dễ hiểu và có tính thẩm mỹ cao"
)


class GeneratedChart(BaseModel):
    """Generated chart output"""
    chart_type: ChartType
    """Type of chart generated"""
    title: str
    """Chart title"""
    description: str
    """Chart description"""
    data_summary: Dict[str, Any]
    """Summary of chart data"""
    insights: List[str]
    """Key insights from the chart"""
    recommendations: List[str]
    """Recommendations based on chart analysis"""
    chart_code: Optional[str] = None
    """Python code to generate the chart"""
    image_data: Optional[str] = None
    """Base64 encoded chart image"""
    
    pass


chart_generator_agent = Agent(
    name="ChartGeneratorAgent",
    instructions=CHART_PROMPT,
    output_type=AgentOutputSchema(GeneratedChart, strict_json_schema=False),
    tools=[
        CodeInterpreterTool(
            tool_config={"type": "code_interpreter", "container": {"type": "auto"}},
        )
    ],
    model=settings.OPENAI_MODEL
)
