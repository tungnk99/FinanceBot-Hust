"""
Response schemas for FinanceBot API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    success: bool = Field(..., description="Whether the request was successful")
    message_id: str = Field(..., description="Unique message ID")
    response: Union[str, Dict[str, Any]] = Field(..., description="Bot response")
    selected_agent: Optional[Dict[str, Any]] = Field(default=None, description="Selected agent info")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    error: Optional[str] = Field(default=None, description="Error message if any")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    version: str = Field(default="1.0.0", description="API version")
    monitoring_enabled: bool = Field(..., description="Whether monitoring is enabled")


class AgentInfo(BaseModel):
    """Agent information model"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    agent_type: str = Field(..., description="Agent type (specialist or task)")


class QueryTypeInfo(BaseModel):
    """Query type information model"""
    value: str = Field(..., description="Query type value")
    description: str = Field(..., description="Query type description")


class AgentsListResponse(BaseModel):
    """Response model for agents list endpoint"""
    specialist_agents: List[AgentInfo] = Field(..., description="List of specialist agents")
    task_agents: List[AgentInfo] = Field(..., description="List of task agents")
    query_types: List[QueryTypeInfo] = Field(..., description="List of supported query types")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Generic success response model"""
    success: bool = Field(default=True, description="Always true for success")
    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data")
