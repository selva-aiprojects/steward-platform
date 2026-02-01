from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseStrategy(ABC):
    """
    Interface for Trading Strategies.
    """
    
    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data and return a signal.
        
        Returns:
            Dict: {
                "signal": "BUY" | "SELL" | "HOLD",
                "confidence": 0.0 - 1.0,
                "rationale": "Explanation..."
            }
        """
        pass
