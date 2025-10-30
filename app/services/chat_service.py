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
            
            # Convert context to dict if it's a ChatContext object
            if isinstance(context, dict):
                context_dict = context
            else:
                # Try different conversion methods
                if hasattr(context, 'model_dump'):
                    context_dict = context.model_dump()
                elif hasattr(context, 'dict'):
                    context_dict = context.dict()
                elif hasattr(context, '__dict__'):
                    context_dict = context.__dict__
                else:
                    # Fallback: create dict from object attributes
                    context_dict = {
                        'deep_research': getattr(context, 'deep_research', False),
                        'attach_files': getattr(context, 'attach_files', [])
                    }
            
            # Create master agent request with default values
            master_request = MasterAgentRequest(
                query=message,
                query_type=None,  # Auto-detect query type
                priority=Priority.MEDIUM,  # Default priority
                context=context_dict,
                user_id=user_id,
                session_id=session_id
            )
            
            # Run master agent

            start_time = datetime.now()
            result = await Runner.run(master_agent, master_request.query)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extract response data
            response_data = result.final_output
            
            # Debug: Print response data type and content
            print(f"🔍 Response data type: {type(response_data)}")
            print(f"🔍 Response data content: {str(response_data)[:200]}...")
            
            # Handle different response types
            if isinstance(response_data, str):
                # String response - clean it for user display
                response_text = self._clean_response_for_user(response_data)
                
                # Extract agent info from original response for metadata
                agent_metadata = self._extract_agent_metadata(response_data)
                selected_agent_info = {
                    "agent_name": agent_metadata.get("agent_name", "FinanceBot"),
                    "agent_type": agent_metadata.get("agent_type", "assistant"),
                    "confidence_score": agent_metadata.get("confidence_score", 0.9),
                    "reasoning": agent_metadata.get("reasoning", "Processed user request"),
                    "execution_time": agent_metadata.get("execution_time", "~1-2 seconds"),
                    "tools_used": agent_metadata.get("tools_used", [])
                }
            elif isinstance(response_data, dict):
                # Check if it's a JSON schema (has $defs property)
                if '$defs' in response_data:
                    print("⚠️  Received JSON schema instead of response data")
                    # Return a simple message for now
                    response_text = "Tôi đang chờ bạn đưa ra yêu cầu tài chính cụ thể. Ví dụ: 'Phân tích cổ phiếu VIC', 'Lấy dữ liệu HOSE cho VIC', 'Đọc báo cáo tài chính VIC 2024', hoặc 'Tạo biểu đồ giá cho VCB'."
                    selected_agent_info = {
                        "agent_name": "none",
                        "agent_type": "none", 
                        "confidence_score": 0.0,
                        "reasoning": "Chưa nhận được yêu cầu tài chính cụ thể. Khi người dùng cho chi tiết, Master Agent sẽ chọn agent phù hợp."
                    }
                else:
                    # Normal dict response
                    response_text = response_data.get('execution_result', str(response_data))
                    if 'selected_agent' in response_data and response_data['selected_agent']:
                        selected_agent_info = response_data['selected_agent']
                    else:
                        selected_agent_info = None
            elif hasattr(response_data, 'model_dump'):
                # Pydantic model - convert to dict
                response_dict = response_data.model_dump()
                response_text = response_dict.get('execution_result', str(response_data))
                if 'selected_agent' in response_dict and response_dict['selected_agent']:
                    selected_agent_info = response_dict['selected_agent']
                else:
                    selected_agent_info = None
            elif hasattr(response_data, 'dict'):
                # Old Pydantic model - convert to dict
                response_dict = response_data.dict()
                response_text = response_dict.get('execution_result', str(response_data))
                if 'selected_agent' in response_dict and response_dict['selected_agent']:
                    selected_agent_info = response_dict['selected_agent']
                else:
                    selected_agent_info = None
            else:
                # Other type
                response_text = str(response_data)
                selected_agent_info = None
            
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
            
            # Return response as object, not string
            final_response = response_text
            
            return {
                "success": True,
                "message_id": message_id,
                "response": final_response,
                "selected_agent": selected_agent_info,
                "execution_time": execution_time,
                "session_id": session_id,
                "timestamp": datetime.now(),
                "metadata": {
                    "agent_name": selected_agent_info.get("agent_name", "FinanceBot"),
                    "agent_type": selected_agent_info.get("agent_type", "assistant"),
                    "confidence_score": selected_agent_info.get("confidence_score", 0.9),
                    "tools_used": selected_agent_info.get("tools_used", []),
                    "processing_time": selected_agent_info.get("execution_time", "~1-2 seconds"),
                    "reasoning": selected_agent_info.get("reasoning", "Processed user request")
                }
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
    
    def _clean_response_for_user(self, response: str) -> str:
        """Clean response to show only user-relevant information"""
        lines = response.split('\n')
        cleaned_lines = []
        
        # Skip internal agent information
        skip_sections = [
            "Dựa trên yêu cầu của bạn",
            "mình đã chọn:",
            "- Agent:",
            "- Lý do:",
            "Kết quả thực thi",
            "Confidence:",
            "Execution time:",
            "Follow-up gợi ý",
            "Bạn có muốn",
            "Muốn mình",
            "Bạn muốn"
        ]
        
        in_result_section = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a section we want to skip
            should_skip = any(line.startswith(skip) for skip in skip_sections)
            
            if should_skip:
                continue
                
            # Look for actual data/results
            if any(keyword in line.lower() for keyword in [
                "giá hiện tại", "biến động", "mở cửa", "khối lượng", 
                "vốn hóa", "thời điểm", "mã cổ phiếu", "sàn"
            ]):
                cleaned_lines.append(line)
            elif line.startswith("- ") and any(keyword in line.lower() for keyword in [
                "vnd", "%", "cổ phiếu", "giá", "cao", "thấp"
            ]):
                cleaned_lines.append(line)
            elif not any(skip in line for skip in skip_sections):
                # Keep lines that don't contain skip patterns
                if len(line) > 10 and not line.startswith("Dựa trên"):
                    cleaned_lines.append(line)
        
        # If we have cleaned results, return them
        if cleaned_lines:
            return '\n'.join(cleaned_lines)
        
        # Fallback: return original response but remove agent selection info
        fallback_lines = []
        for line in lines:
            if not any(skip in line for skip in skip_sections):
                fallback_lines.append(line)
        
        return '\n'.join(fallback_lines) if fallback_lines else response

    def _extract_agent_metadata(self, response: str) -> dict:
        """Extract agent metadata from response for internal tracking"""
        metadata = {
            "agent_name": "FinanceBot",
            "agent_type": "assistant", 
            "confidence_score": 0.9,
            "reasoning": "Processed user request",
            "execution_time": "~1-2 seconds",
            "tools_used": []
        }
        
        lines = response.split('\n')
        
        # Look for agent information
        for line in lines:
            line = line.strip()
            
            # Extract agent name
            if "- Agent:" in line:
                agent_name = line.split("- Agent:")[-1].strip()
                if agent_name and agent_name != "FinanceBot":
                    metadata["agent_name"] = agent_name
                    metadata["agent_type"] = "specialist" if "agent" in agent_name.lower() else "tool"
            
            # Extract confidence score
            if "Confidence:" in line:
                try:
                    confidence = float(line.split("Confidence:")[-1].strip())
                    metadata["confidence_score"] = confidence
                except:
                    pass
            
            # Extract execution time
            if "Execution time:" in line:
                exec_time = line.split("Execution time:")[-1].strip()
                metadata["execution_time"] = exec_time
            
            # Extract tools used
            if "tools" in line.lower() or "tool" in line.lower():
                if "get_realtime_market_data" in line:
                    metadata["tools_used"].append("market_data")
                if "get_crypto_market_data" in line:
                    metadata["tools_used"].append("crypto_data")
                if "get_stock_with_technical_analysis" in line:
                    metadata["tools_used"].append("technical_analysis")
                if "research_agent" in line:
                    metadata["tools_used"].append("research")
                if "quant_agent" in line:
                    metadata["tools_used"].append("quantitative")
                if "chart_generator" in line:
                    metadata["tools_used"].append("chart_generation")
        
        return metadata

    def shutdown(self):
        """Shutdown the service"""
        if self.monitor:
            self.monitor.shutdown()
