from typing import Dict, List, Any
from app.services.broker.base import BrokerInterface

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
        from app.models.portfolio import Portfolio, Holding
        from app.core.database import SessionLocal
        
        db = self.db or SessionLocal()
        total_cost = quantity * price
        
        try:
            # 1. Update Portfolio Balance
            portfolio = db.query(Portfolio).filter(Portfolio.id == self.portfolio_id).first()
            if not portfolio:
                raise Exception(f"Portfolio {self.portfolio_id} not found")

            # 2. Update Holding
            holding = db.query(Holding).filter(Holding.portfolio_id == self.portfolio_id, Holding.symbol == symbol).first()
            
            if action == "BUY":
                if portfolio.cash_balance < total_cost:
                    raise Exception("Insufficient funds")
                
                portfolio.cash_balance -= total_cost
                portfolio.invested_amount += total_cost
                
                if not holding:
                    holding = Holding(
                        portfolio_id=self.portfolio_id,
                        symbol=symbol,
                        quantity=quantity,
                        avg_price=price,
                        current_price=price,
                        pnl=0.0,
                        pnl_pct=0.0
                    )
                    db.add(holding)
                else:
                    new_total_qty = holding.quantity + quantity
                    new_avg_price = ((holding.avg_price * holding.quantity) + (price * quantity)) / new_total_qty
                    holding.quantity = new_total_qty
                    holding.avg_price = new_avg_price
                    holding.current_price = price # Update with execution price
            else: # SELL
                if not holding or holding.quantity < quantity:
                    raise Exception(f"Insufficient holdings of {symbol}")
                
                portfolio.cash_balance += total_cost
                portfolio.invested_amount -= (holding.avg_price * quantity) # Reduce invested by cost basis
                
                holding.quantity -= quantity
                holding.current_price = price
                if holding.quantity == 0:
                    db.delete(holding)
            
            # 3. Record Trade
            trade = Trade(
                user_id=portfolio.user_id,
                portfolio_id=self.portfolio_id,
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                status="EXECUTED",
                execution_mode="PAPER_TRADING"
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
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if not self.db:
                db.close()

    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Return list of current holdings for the portfolio.
        """
        from app.models.portfolio import Holding
        from app.core.database import SessionLocal

        db = self.db or SessionLocal()
        try:
            holdings = db.query(Holding).filter(Holding.portfolio_id == self.portfolio_id).all()
            return [
                {
                    "symbol": h.symbol,
                    "quantity": h.quantity,
                    "avg_price": h.avg_price,
                    "current_price": h.current_price,
                    "pnl": h.pnl,
                    "pnl_pct": h.pnl_pct,
                }
                for h in holdings
            ]
        finally:
            if not self.db:
                db.close()

    async def get_pnl(self) -> Dict[str, float]:
        """
        Return portfolio-level cash and holding PnL.
        """
        from app.models.portfolio import Portfolio, Holding
        from app.core.database import SessionLocal

        db = self.db or SessionLocal()
        try:
            portfolio = db.query(Portfolio).filter(Portfolio.id == self.portfolio_id).first()
            if not portfolio:
                raise Exception(f"Portfolio {self.portfolio_id} not found")
            holdings = db.query(Holding).filter(Holding.portfolio_id == self.portfolio_id).all()
            unrealized_pnl = sum(float(h.pnl or 0.0) for h in holdings)
            return {
                "realized_pnl": 0.0,
                "unrealized_pnl": unrealized_pnl,
                "cash_balance": float(portfolio.cash_balance or 0.0),
            }
        finally:
            if not self.db:
                db.close()
