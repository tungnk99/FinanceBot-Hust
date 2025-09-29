"""
Base classes for agents
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class RunContextWrapper(BaseModel):
    """Wrapper for run context"""
    context: Dict[str, Any] = {}
    
    def __init__(self, **data):
        super().__init__(**data)


class FunctionTool(BaseModel):
    """Function tool definition"""
    name: str
    description: str
    params_json_schema: Dict[str, Any]
    on_invoke_tool: callable
    
    class Config:
        arbitrary_types_allowed = True


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.model = None
    
    def get_model(self):
        """Lấy model"""
        return self.model
    
    @abstractmethod
    async def run(self, context: RunContextWrapper) -> Any:
        """Run the agent with given context"""
        pass
