from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models.state import PhotoSystemState


class BaseNode(ABC):
    """Base class for LangGraph nodes"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def execute(self, state: PhotoSystemState) -> PhotoSystemState:
        """Execute node logic"""
        pass
    
    def _log(self, message: str, level: str = "INFO"):
        """Log messages"""
        print(f"[{level}] {self.name}: {message}")
        
    def _update_state(self, state: PhotoSystemState, **updates) -> PhotoSystemState:
        """Helper method to update state"""
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state
