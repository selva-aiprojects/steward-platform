from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BrokerInterface(ABC):
    """
    Abstract Interface for Broker interactions.
    Allows swapping between Paper Trading and Real Brokers (IBKR, Alpaca, etc).
    """

    @abstractmethod
    async def place_order(self, symbol: str, quantity: int, action: str, price: float, order_type: str = "MARKET") -> Dict[str, Any]:
        """
        Place a buy/sell order.
        """
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current open positions.
        """
        pass

    @abstractmethod
    async def get_pnl(self) -> Dict[str, float]:
        """
        Get Realized and Unrealized PnL.
        """
        pass
