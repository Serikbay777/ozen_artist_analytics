"""
Base Tool class for all analytics tools
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Parameter definition for a tool"""
    name: str
    type: str  # "string", "integer", "boolean"
    description: str
    required: bool = False
    default: Any = None


class BaseTool(ABC):
    """
    Base class for all analytics tools.
    Each tool provides specific analytics functionality.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the tool"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does"""
        pass
    
    @property
    def parameters(self) -> List[ToolParameter]:
        """List of parameters this tool accepts"""
        return []
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.
        Returns a dictionary with results.
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary for LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default
                }
                for p in self.parameters
            ]
        }
    
    def __str__(self) -> str:
        params_str = ", ".join([f"{p.name}: {p.type}" for p in self.parameters])
        return f"{self.name}({params_str}) - {self.description}"

