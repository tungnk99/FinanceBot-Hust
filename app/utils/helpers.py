"""
Helper utilities for FinanceBot API
"""
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


def generate_message_id() -> str:
    """Generate a unique message ID"""
    return str(uuid.uuid4())


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """Get current timestamp"""
    return datetime.now()


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """
    Format error message for API response
    
    Args:
        error: Exception object
        context: Additional context
        
    Returns:
        str: Formatted error message
    """
    error_msg = str(error)
    
    if context:
        error_msg = f"{context}: {error_msg}"
    
    return error_msg


def extract_agent_info(result_output: Any) -> Optional[Dict[str, Any]]:
    """
    Extract agent information from result output
    
    Args:
        result_output: Result output from agent
        
    Returns:
        Optional[Dict]: Agent information or None
    """
    if not hasattr(result_output, 'selected_agent'):
        return None
    
    selected_agent = result_output.selected_agent
    
    return {
        "agent_name": getattr(selected_agent, 'agent_name', 'Unknown'),
        "agent_type": getattr(selected_agent, 'agent_type', 'Unknown'),
        "confidence_score": getattr(selected_agent, 'confidence_score', 0.0),
        "reasoning": getattr(selected_agent, 'reasoning', 'No reasoning provided')
    }


def calculate_execution_time(start_time: datetime, end_time: Optional[datetime] = None) -> float:
    """
    Calculate execution time in seconds
    
    Args:
        start_time: Start time
        end_time: End time (defaults to now)
        
    Returns:
        float: Execution time in seconds
    """
    if end_time is None:
        end_time = datetime.now()
    
    return (end_time - start_time).total_seconds()


def create_context_dict(
    symbol: Optional[str] = None,
    analysis_type: Optional[str] = None,
    timeframe: Optional[str] = None,
    indicators: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create context dictionary for requests
    
    Args:
        symbol: Stock symbol
        analysis_type: Type of analysis
        timeframe: Analysis timeframe
        indicators: Technical indicators
        **kwargs: Additional context data
        
    Returns:
        Dict: Context dictionary
    """
    context = {}
    
    if symbol:
        context["symbol"] = symbol
    if analysis_type:
        context["analysis_type"] = analysis_type
    if timeframe:
        context["timeframe"] = timeframe
    if indicators:
        context["indicators"] = indicators
    
    # Add any additional context
    context.update(kwargs)
    
    return context


def format_response_text(response: Any) -> str:
    """
    Format response text from agent output
    
    Args:
        response: Response from agent
        
    Returns:
        str: Formatted response text
    """
    if response is None:
        return "No response received"
    
    # If it's already a string, return as is
    if isinstance(response, str):
        return response
    
    # Try to convert to string
    try:
        return str(response)
    except Exception:
        return "Unable to format response"


def log_api_call(
    monitor,
    event_type: str,
    data: Dict[str, Any]
) -> None:
    """
    Log API call to monitoring system
    
    Args:
        monitor: Monitoring instance
        event_type: Type of event
        data: Event data
    """
    if monitor and monitor.is_configured:
        monitor.log_event(event_type, data)


def create_error_response(
    error: str,
    message_id: Optional[str] = None,
    session_id: Optional[str] = None,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error response
    
    Args:
        error: Error message
        message_id: Message ID
        session_id: Session ID
        error_code: Error code
        details: Additional details
        
    Returns:
        Dict: Error response
    """
    response = {
        "success": False,
        "error": error,
        "timestamp": get_current_timestamp()
    }
    
    if message_id:
        response["message_id"] = message_id
    if session_id:
        response["session_id"] = session_id
    if error_code:
        response["error_code"] = error_code
    if details:
        response["details"] = details
    
    return response


def create_success_response(
    response_text: str,
    message_id: str,
    session_id: Optional[str] = None,
    selected_agent: Optional[Dict[str, Any]] = None,
    execution_time: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create standardized success response
    
    Args:
        response_text: Response text
        message_id: Message ID
        session_id: Session ID
        selected_agent: Selected agent info
        execution_time: Execution time
        
    Returns:
        Dict: Success response
    """
    response = {
        "success": True,
        "message_id": message_id,
        "response": response_text,
        "timestamp": get_current_timestamp()
    }
    
    if session_id:
        response["session_id"] = session_id
    if selected_agent:
        response["selected_agent"] = selected_agent
    if execution_time:
        response["execution_time"] = execution_time
    
    return response


def validate_json_payload(payload: str) -> Optional[Dict[str, Any]]:
    """
    Validate and parse JSON payload
    
    Args:
        payload: JSON string to validate
        
    Returns:
        Optional[Dict]: Parsed JSON or None if invalid
    """
    try:
        return json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return None


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."
