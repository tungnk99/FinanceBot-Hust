"""
API Routes for FinanceBot FastAPI Service
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.schemas.requests import ChatRequest
from app.schemas.responses import ChatResponse, HealthResponse
from app.services.chat_service import ChatService

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
            session_id=request.session_id,
            user_id=request.user_id,
            context=request.context
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")



