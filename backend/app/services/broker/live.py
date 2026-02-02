from typing import Dict, List, Any
from app.services.broker.base import BrokerInterface
from app.services.kite_service import kite_service
import logging

logger = logging.getLogger(__name__)

class LiveBrokerAdapter(BrokerInterface):
    """
    Zerodha Kite Broker Adapter.
    Used ONLY in LIVE_TRADING mode.
    """

    async def place_order(self, symbol: str, quantity: int, action: str, price: float, order_type: str = "MARKET") -> Dict[str, Any]:
        """
        Place real order via Zerodha Kite API.
        """
        kite = kite_service.get_client()
        if not kite:
            raise Exception("Kite client not initialized. Check API keys and Access Token.")
            
        try:
            # Zerodha specific order placement
            # Note: Using MARKET order by default if order_type is MARKET
            order_params = {
                "variety": kite.VARIETY_REGULAR,
                "exchange": kite.EXCHANGE_NSE,
                "tradingsymbol": symbol,
                "transaction_type": kite.TRANSACTION_TYPE_BUY if action.upper() == "BUY" else kite.TRANSACTION_TYPE_SELL,
                "quantity": int(quantity),
                "product": kite.PRODUCT_CNC, # Cash & Carry for equity
                "order_type": kite.ORDER_TYPE_MARKET if order_type.upper() == "MARKET" else kite.ORDER_TYPE_LIMIT,
                "price": float(price) if order_type.upper() == "LIMIT" else None
            }
            
            logger.info(f"Placing live order: {order_params}")
            order_id = kite.place_order(**order_params)
            
            return {
                "order_id": order_id,
                "status": "SUBMITTED",
                "symbol": symbol,
                "quantity": quantity,
                "action": action,
                "timestamp": None # Zerodha usually returns order_id first
            }
        except Exception as e:
            logger.error(f"Kite order placement failed: {e}")
            raise Exception(f"Kite API Error: {e}")

    async def get_positions(self) -> List[Dict[str, Any]]:
        kite = kite_service.get_client()
        if not kite:
            return []
        try:
            return kite.positions().get("net", [])
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def get_pnl(self) -> Dict[str, float]:
        # Simple PnL summary from positions
        positions = await self.get_positions()
        total_pnl = sum(p.get("pnl", 0.0) for p in positions)
        return {"realized": 0.0, "unrealized": total_pnl}
