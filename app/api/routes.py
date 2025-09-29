"""
API Routes for FinanceBot FastAPI Service
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.schemas.requests import ChatRequest, StockAnalysisRequest, ChartRequest
from app.schemas.responses import ChatResponse, HealthResponse, AgentsListResponse
from app.services.chat_service import ChatService
from app.utils.helpers import generate_message_id
from app.utils.validators import validate_stock_symbol

# Create router
router = APIRouter()

# Global chat service
chat_service = None


async def get_chat_service():
    """Dependency to get chat service instance"""
    global chat_service
    if not chat_service:
        chat_service = ChatService()
    return chat_service


@router.get("/health", response_model=HealthResponse)
async def health_check(service: ChatService = Depends(get_chat_service)):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        monitoring_enabled=service.monitor.is_configured if service.monitor else False
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Main chat endpoint - processes user messages through Master Agent
    """
    try:
        result = await service.process_chat_message(
            message=request.message,
            query_type=request.query_type,
            priority=request.priority,
            session_id=request.session_id,
            user_id=request.user_id,
            context=request.context
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/analyze/stock", response_model=ChatResponse)
async def analyze_stock(
    request: StockAnalysisRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Stock analysis endpoint
    """
    # Validate stock symbol
    if not validate_stock_symbol(request.symbol):
        raise HTTPException(status_code=400, detail="Invalid stock symbol format")
    
    try:
        result = await service.analyze_stock(
            symbol=request.symbol,
            analysis_type=request.analysis_type,
            timeframe=request.timeframe,
            indicators=request.indicators
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock analysis failed: {str(e)}")


@router.post("/analyze/quantitative", response_model=ChatResponse)
async def quantitative_analysis(
    request: StockAnalysisRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Quantitative analysis endpoint
    """
    # Validate stock symbol
    if not validate_stock_symbol(request.symbol):
        raise HTTPException(status_code=400, detail="Invalid stock symbol format")
    
    try:
        result = await service.quantitative_analysis(
            symbol=request.symbol,
            indicators=request.indicators,
            timeframe=request.timeframe
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quantitative analysis failed: {str(e)}")


@router.post("/generate/chart", response_model=ChatResponse)
async def generate_chart(
    request: ChartRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Chart generation endpoint
    """
    # Validate stock symbol
    if not validate_stock_symbol(request.symbol):
        raise HTTPException(status_code=400, detail="Invalid stock symbol format")
    
    try:
        result = await service.generate_chart(
            symbol=request.symbol,
            chart_type=request.chart_type,
            timeframe=request.timeframe
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(e)}")


@router.get("/agents", response_model=AgentsListResponse)
async def list_agents():
    """
    List available agents and their capabilities
    """
    return AgentsListResponse(
        specialist_agents=[
            {
                "name": "research_agent",
                "description": "Nghiên cứu cổ phiếu toàn diện với phân tích cơ bản, kỹ thuật và thị trường",
                "capabilities": ["stock_research", "fundamental_analysis", "market_analysis"],
                "agent_type": "specialist"
            },
            {
                "name": "quant_agent", 
                "description": "Phân tích định lượng, kỹ thuật và tính toán các metrics tài chính",
                "capabilities": ["technical_analysis", "quantitative_metrics", "risk_calculation"],
                "agent_type": "specialist"
            },
            {
                "name": "fin_doc_agent",
                "description": "Đọc và phân tích báo cáo tài chính, trích xuất dữ liệu",
                "capabilities": ["document_analysis", "financial_reports", "data_extraction"],
                "agent_type": "specialist"
            },
            {
                "name": "risk_agent",
                "description": "Đánh giá rủi ro toàn diện và phân tích các yếu tố rủi ro",
                "capabilities": ["risk_assessment", "volatility_analysis", "risk_mitigation"],
                "agent_type": "specialist"
            }
        ],
        task_agents=[
            {
                "name": "search_agent",
                "description": "Tìm kiếm thông tin tài chính từ nhiều nguồn dữ liệu",
                "capabilities": ["information_retrieval", "market_data", "news_search"],
                "agent_type": "task"
            },
            {
                "name": "chart_generator_agent",
                "description": "Tạo biểu đồ tài chính chuyên nghiệp và visualizations",
                "capabilities": ["chart_generation", "data_visualization", "technical_charts"],
                "agent_type": "task"
            },
            {
                "name": "writer_agent",
                "description": "Viết báo cáo tài chính chuyên nghiệp và comprehensive analysis",
                "capabilities": ["report_writing", "analysis_synthesis", "investment_recommendations"],
                "agent_type": "task"
            }
        ],
        query_types=[
            {"value": "stock_research", "description": "Nghiên cứu cổ phiếu toàn diện"},
            {"value": "quantitative_analysis", "description": "Phân tích định lượng và kỹ thuật"},
            {"value": "financial_document", "description": "Phân tích tài liệu tài chính"},
            {"value": "risk_assessment", "description": "Đánh giá rủi ro"},
            {"value": "market_search", "description": "Tìm kiếm thông tin thị trường"},
            {"value": "chart_generation", "description": "Tạo biểu đồ"},
            {"value": "report_writing", "description": "Viết báo cáo"},
            {"value": "comprehensive_analysis", "description": "Phân tích toàn diện"},
            {"value": "general_finance", "description": "Câu hỏi tài chính chung"}
        ]
    )