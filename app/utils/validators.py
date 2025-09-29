"""
Validation utilities for FinanceBot API
"""
import re
from typing import List, Optional


def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Check length (1-10 characters)
    if len(symbol) < 1 or len(symbol) > 10:
        return False
    
    # Check format (letters and numbers only)
    if not re.match(r'^[A-Z0-9]+$', symbol):
        return False
    
    return True


def validate_timeframe(timeframe: str) -> bool:
    """
    Validate timeframe format
    
    Args:
        timeframe: Timeframe to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_timeframes = [
        "1 month", "3 months", "6 months", 
        "1 year", "2 years", "5 years"
    ]
    
    return timeframe in valid_timeframes


def validate_indicators(indicators: List[str]) -> bool:
    """
    Validate technical indicators list
    
    Args:
        indicators: List of indicators to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(indicators, list):
        return False
    
    # Check maximum number of indicators
    if len(indicators) > 10:
        return False
    
    valid_indicators = [
        "RSI", "MACD", "Moving Averages", "Bollinger Bands",
        "Stochastic", "CCI", "Williams %R", "ADX", "ATR",
        "Volume", "Price", "Support", "Resistance"
    ]
    
    for indicator in indicators:
        if not isinstance(indicator, str) or indicator not in valid_indicators:
            return False
    
    return True


def validate_message_length(message: str, max_length: int = 1000) -> bool:
    """
    Validate message length
    
    Args:
        message: Message to validate
        max_length: Maximum allowed length
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not message or not isinstance(message, str):
        return False
    
    return len(message.strip()) <= max_length


def validate_session_id(session_id: Optional[str]) -> bool:
    """
    Validate session ID format
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if session_id is None:
        return True  # Optional field
    
    if not isinstance(session_id, str):
        return False
    
    # Check UUID format
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, session_id, re.IGNORECASE))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input
    
    Args:
        text: Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Trim whitespace
    return sanitized.strip()


def validate_analysis_type(analysis_type: str) -> bool:
    """
    Validate analysis type
    
    Args:
        analysis_type: Analysis type to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_types = [
        "comprehensive", "technical", "fundamental", "quick"
    ]
    
    return analysis_type in valid_types


def validate_report_type(report_type: str) -> bool:
    """
    Validate report type
    
    Args:
        report_type: Report type to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_types = [
        "investment analysis", "earnings report", 
        "market outlook", "risk report"
    ]
    
    return report_type in valid_types


def validate_target_audience(audience: str) -> bool:
    """
    Validate target audience
    
    Args:
        audience: Target audience to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_audiences = [
        "general", "professional", "beginner", "expert"
    ]
    
    return audience in valid_audiences
