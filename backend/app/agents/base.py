from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAgent(ABC):
    """
    Abstract Base Class for all StockSteward AI Agents.
    
    The Framework Contract:
    1. Agents receive a `context` dictionary.
    2. Agents return a structured dictionary output.
    3. Agents DO NOT call other agents directly.
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's logic.
        
        Args:
            context: Shared state/data required for execution.
            
        Returns:
            Dict containing the agent's output/findings to be merged back into context.
        """
        pass

    async def health_check(self) -> bool:
        """
        Basic health check for the agent.
        """
        return True
