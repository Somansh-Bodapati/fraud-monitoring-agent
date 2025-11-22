"""
Base agent class for all agents in the system
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logs = []
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Dictionary with results and metadata
        """
        pass
    
    def log(self, message: str, level: str = "INFO", data: Optional[Dict] = None):
        """Log agent activity"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name,
            "level": level,
            "message": message,
            "data": data or {},
        }
        self.logs.append(log_entry)
        return log_entry
    
    def get_logs(self) -> list:
        """Get all logs for this agent"""
        return self.logs
    
    def clear_logs(self):
        """Clear agent logs"""
        self.logs = []
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"

