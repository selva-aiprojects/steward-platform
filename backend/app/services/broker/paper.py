from typing import Dict, List, Any
from app.services.broker.base import BrokerInterface
import uuid
from datetime import datetime

class PaperTradingEngine(BrokerInterface):
    """
    Simulated Broker Engine.
    Maintains virtual positions and calculates PnL.
    
    NOTE: Persists state to the 'portfolios' and 'trades' tables in the database.
    """
    
    def __init__(self, portfolio_id: int, db_session=None):
        self.portfolio_id = portfolio_id
        self.db = db_session


    async def place_order(self, symbol: str, quantity: int, action: str, price: float, order_type: str = "MARKET") -> Dict[str, Any]:
        from app.models.trade import Trade
        from app.models.portfolio import Portfolio
        from app.core.database import SessionLocal
        
        db = self.db or SessionLocal()
        total_cost = quantity * price
        
        try:
            # 1. Update Portfolio Balance
            portfolio = db.query(Portfolio).filter(Portfolio.id == self.portfolio_id).first()
            if action == "BUY":
                portfolio.cash_balance -= total_cost
                portfolio.invested_amount += total_cost
            else: # SELL
                portfolio.cash_balance += total_cost
                portfolio.invested_amount -= total_cost
            
            # 2. Record Trade
            trade = Trade(
                portfolio_id=self.portfolio_id,
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                status="EXECUTED",
                execution_mode="PAPER"
            )
            db.add(trade)
            db.add(portfolio)
            db.commit()
            db.refresh(trade)
            
            return {
                "order_id": str(trade.id),
                "status": "FILLED",
                "filled_price": price,
                "filled_quantity": quantity,
                "timestamp": trade.timestamp.isoformat()
            }
        finally:
            if not self.db:
                db.close()

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
