from typing import Dict, List, Any
from app.services.broker.base import BrokerInterface
import uuid
from datetime import datetime

class PaperTradingEngine(BrokerInterface):
    """
    Simulated Broker Engine.
    Maintains virtual positions and calculates PnL.
    
    NOTE: In a real implementation, this would persist state to the 'portfolios' and 'trades' tables.
    For this scaffold, we use an in-memory structure or assume stateless per request (mock).
    To fully satisfy requirements, we'll simulate state management.
    """
    
    def __init__(self):
        # In-memory storage for the simulation session
        # In production, load this from DB
        self._positions: Dict[str, Dict[str, Any]] = {} 
        self._trades: List[Dict[str, Any]] = []
        self._cash_balance = 100000.0  # Starting paper cash
        self._realized_pnl = 0.0

    async def place_order(self, symbol: str, quantity: int, action: str, price: float, order_type: str = "MARKET") -> Dict[str, Any]:
        """
        Simulate order execution.
        """
        total_cost = quantity * price
        
        trade_record = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "quantity": quantity,
            "action": action,
            "price": price,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "FILLED"
        }
        
        self._trades.append(trade_record)
        
        # Update Positions Logic
        if symbol not in self._positions:
            self._positions[symbol] = {"quantity": 0, "avg_price": 0.0}
            
        pos = self._positions[symbol]
        
        if action == "BUY":
            # Update weighted average price
            current_qty = pos["quantity"]
            current_cost = current_qty * pos["avg_price"]
            new_cost = total_cost
            
            new_qty = current_qty + quantity
            if new_qty > 0:
                pos["avg_price"] = (current_cost + new_cost) / new_qty
            
            pos["quantity"] = new_qty
            self._cash_balance -= total_cost
            
        elif action == "SELL":
            # Calculate Realized PnL based on Avg Price
            avg_price = pos["avg_price"]
            pnl_per_share = price - avg_price
            trade_pnl = pnl_per_share * quantity
            
            self._realized_pnl += trade_pnl
            self._cash_balance += total_cost
            
            pos["quantity"] -= quantity
            if pos["quantity"] <= 0:
                del self._positions[symbol]
        
        return {
            "order_id": trade_record["id"],
            "status": "FILLED",
            "filled_price": price,
            "filled_quantity": quantity,
            "commission": 0.0  # Free paper trading
        }

    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Return list of positions.
        """
        positions_list = []
        for sym, data in self._positions.items():
            positions_list.append({
                "symbol": sym,
                "quantity": data["quantity"],
                "avg_price": data["avg_price"]
            })
        return positions_list

    async def get_pnl(self) -> Dict[str, float]:
        """
        Calculate PnL.
        NOTE: Unrealized requires current market price. Passing 0 or mock for now as engine 
        doesn't inherently know market price without an input or fetch.
        """
        return {
            "realized_pnl": self._realized_pnl,
            "unrealized_pnl": 0.0,  # Needs current market price feeds to calculate
            "cash_balance": self._cash_balance
        }
