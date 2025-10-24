"""
Chat Service - Business logic for chat operations
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import json

from app.core.config import get_settings
from app.monitors.model_monitor import create_monitor
from src.agents.planner_agents.master_agent import master_agent, MasterAgentRequest, Priority
from agents import Runner
# from src.agents import Runner  # Removed - not needed


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
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message through Master Agent
        
        Args:
            message: User message
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
                    "message_length": len(message)
                })
            
            # Create master agent request with default values
            master_request = MasterAgentRequest(
                query=message,
                query_type=None,  # Auto-detect query type
                priority=Priority.MEDIUM,  # Default priority
                context=context,
                user_id=user_id,
                session_id=session_id
            )
            
            # Run master agent
            start_time = datetime.now()
            result = await Runner.run(master_agent, message)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extract response data
            response_data = result.final_output
            
            # Handle different response types
            if hasattr(response_data, 'model_dump'):
                # Pydantic model - convert to dict
                response_dict = response_data.model_dump()
                response_text = response_dict.get('execution_result', str(response_data))
            elif hasattr(response_data, 'dict'):
                # Old Pydantic model - convert to dict
                response_dict = response_data.dict()
                response_text = response_dict.get('execution_result', str(response_data))
            elif isinstance(response_data, dict):
                # Already a dict
                response_text = response_data.get('execution_result', str(response_data))
            else:
                # String or other type
                response_text = str(response_data)
            
            # Extract agent info if available
            selected_agent_info = None
            if hasattr(response_data, 'selected_agent') and response_data.selected_agent:
                selected_agent_info = {
                    "agent_name": getattr(response_data.selected_agent, 'agent_name', 'Unknown'),
                    "agent_type": getattr(response_data.selected_agent, 'agent_type', 'Unknown'),
                    "confidence_score": getattr(response_data.selected_agent, 'confidence_score', 0.0),
                    "reasoning": getattr(response_data.selected_agent, 'reasoning', 'No reasoning provided')
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
            
            # Ensure response is JSON serializable
            try:
                # Try to serialize response_text to ensure it's JSON compatible
                if isinstance(response_text, str):
                    # If it's a string, try to parse as JSON first
                    try:
                        json.loads(response_text)
                        final_response = response_text
                    except (json.JSONDecodeError, TypeError):
                        # If not valid JSON, wrap it in a JSON string
                        final_response = json.dumps({"message": response_text})
                else:
                    # Convert to JSON string
                    final_response = json.dumps(response_text)
            except Exception:
                # Fallback to string representation
                final_response = str(response_text)
            
            return {
                "success": True,
                "message_id": message_id,
                "response": final_response,
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
                    "query_type": "auto"
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
            context=context
        )
    
    def shutdown(self):
        """Shutdown the service"""
        if self.monitor:
            self.monitor.shutdown()
