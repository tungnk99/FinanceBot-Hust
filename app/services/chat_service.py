"""
Chat Service - Business logic for chat operations
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.core.config import get_settings
from app.monitors import create_monitor
from src.agents.planner_agents.master_agent import master_agent, MasterAgentRequest, QueryType, Priority
from agents import Runner


class ChatService:
    """Service for handling chat operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.monitor = create_monitor(self.settings, self.settings.monitoring_provider)
        if self.monitor.initialize():
            print("✅ ChatService monitoring initialized")
        else:
            print("⚠️  ChatService monitoring initialization failed")
    
    async def process_chat_message(
        self,
        message: str,
        query_type: Optional[QueryType] = None,
        priority: Priority = Priority.MEDIUM,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message through Master Agent
        
        Args:
            message: User message
            query_type: Type of query
            priority: Priority level
            session_id: Session ID
            user_id: User ID
            context: Additional context
        
        Returns:
            Dict containing response and metadata
        """
        message_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())
        context = context or {}
        
        try:
            print(f"📝 Processing chat message: {message[:100]}...")
            
            # Log chat event
            if self.monitor and self.monitor.is_configured:
                self.monitor.log_event("chat_request", {
                    "message_id": message_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "query_type": query_type.value if query_type else "auto",
                    "priority": priority.value,
                    "message_length": len(message)
                })
            
            # Create master agent request
            master_request = MasterAgentRequest(
                query=message,
                query_type=query_type,
                priority=priority,
                context=context,
                user_id=user_id,
                session_id=session_id
            )
            
            # Run master agent
            start_time = datetime.now()
            result = await Runner.run(master_agent, message)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extract response as JSON object
            response_data = result.final_output
            
            # Convert to dict if it's a Pydantic model
            if hasattr(response_data, 'model_dump'):
                response_data = response_data.model_dump()
            elif hasattr(response_data, 'dict'):
                response_data = response_data.dict()
            else:
                # If it's not a Pydantic model, convert to string
                response_data = str(response_data)
            
            selected_agent_info = None
            
            if hasattr(result.final_output, 'selected_agent'):
                selected_agent_info = {
                    "agent_name": getattr(result.final_output.selected_agent, 'agent_name', 'Unknown'),
                    "agent_type": getattr(result.final_output.selected_agent, 'agent_type', 'Unknown'),
                    "confidence_score": getattr(result.final_output.selected_agent, 'confidence_score', 0.0),
                    "reasoning": getattr(result.final_output.selected_agent, 'reasoning', 'No reasoning provided')
                }
            
            # Log success
            if self.monitor and self.monitor.is_configured:
                self.monitor.log_event("chat_success", {
                    "message_id": message_id,
                    "session_id": session_id,
                    "execution_time": execution_time,
                    "selected_agent": selected_agent_info["agent_name"] if selected_agent_info else "Unknown",
                    "response_length": len(str(response_data))
                })
            
            # Flush traces
            if self.monitor and self.monitor.is_configured:
                self.monitor.flush()
            
            return {
                "success": True,
                "message_id": message_id,
                "response": response_data,
                "selected_agent": selected_agent_info,
                "execution_time": execution_time,
                "session_id": session_id,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            print(f"❌ Chat error: {e}")
            
            # Log error
            if self.monitor and self.monitor.is_configured:
                self.monitor.log_event("chat_error", {
                    "message_id": message_id,
                    "session_id": session_id,
                    "error": str(e),
                    "query_type": query_type.value if query_type else "auto"
                })
                self.monitor.flush()
            
            return {
                "success": False,
                "message_id": message_id,
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now()
            }
    
    async def analyze_stock(
        self,
        symbol: str,
        analysis_type: str = "comprehensive",
        timeframe: str = "1 year",
        indicators: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Perform stock analysis
        
        Args:
            symbol: Stock symbol
            analysis_type: Type of analysis
            timeframe: Analysis timeframe
            indicators: Technical indicators
        
        Returns:
            Dict containing analysis results
        """
        query = f"Phân tích cổ phiếu {symbol} - {analysis_type} analysis"
        
        context = {
            "symbol": symbol,
            "analysis_type": analysis_type,
            "timeframe": timeframe,
            "indicators": indicators
        }
        
        return await self.process_chat_message(
            message=query,
            query_type=QueryType.STOCK_RESEARCH,
            priority=Priority.HIGH,
            context=context
        )
    
    async def quantitative_analysis(
        self,
        symbol: str,
        indicators: list = None,
        timeframe: str = "1 year"
    ) -> Dict[str, Any]:
        """
        Perform quantitative analysis
        
        Args:
            symbol: Stock symbol
            indicators: Technical indicators
            timeframe: Analysis timeframe
        
        Returns:
            Dict containing quantitative analysis results
        """
        if indicators is None:
            indicators = ["RSI", "MACD", "Moving Averages"]
        
        indicators_str = ", ".join(indicators)
        query = f"Tính {indicators_str} cho cổ phiếu {symbol}"
        
        context = {
            "symbol": symbol,
            "indicators": indicators,
            "timeframe": timeframe
        }
        
        return await self.process_chat_message(
            message=query,
            query_type=QueryType.QUANTITATIVE_ANALYSIS,
            priority=Priority.MEDIUM,
            context=context
        )
    
    async def generate_chart(
        self,
        symbol: str,
        chart_type: str = "price with moving averages",
        timeframe: str = "1 year"
    ) -> Dict[str, Any]:
        """
        Generate financial chart
        
        Args:
            symbol: Stock symbol
            chart_type: Type of chart
            timeframe: Chart timeframe
        
        Returns:
            Dict containing chart generation results
        """
        query = f"Tạo biểu đồ {chart_type} cho cổ phiếu {symbol}"
        
        context = {
            "symbol": symbol,
            "chart_type": chart_type,
            "timeframe": timeframe
        }
        
        return await self.process_chat_message(
            message=query,
            query_type=QueryType.CHART_GENERATION,
            priority=Priority.MEDIUM,
            context=context
        )
    
    def shutdown(self):
        """Shutdown the service"""
        if self.monitor:
            self.monitor.shutdown()
