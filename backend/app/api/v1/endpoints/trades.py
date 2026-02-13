from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from app.api.v1 import deps
from app import schemas
import random
from datetime import datetime, timedelta

router = APIRouter()

from sqlalchemy.orm import Session
from app.core.database import get_db
from app import models
from app.core.rbac import get_current_user

@router.get("/", response_model=List[schemas.TradeResponse])
def list_trades(
    db: Session = Depends(get_db),
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve trades.
    """
    query = db.query(models.trade.Trade)
    if user_id:
        query = query.join(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == user_id)
    
    trades = query.offset(skip).limit(limit).all()
    return trades

@router.post("/", response_model=schemas.TradeResult)
async def execute_trade_endpoint(proposal: schemas.TradeProposal) -> Any:
    """
    Execute a trade. 
    This is the standard endpoint hit by the frontend 'executeTrade' service.
    """
    from app.services.trade_service import TradeService
    trade_dict = proposal.model_dump()
    if not trade_dict.get("price"):
        trade_dict["price"] = 100.0
        
    service = TradeService()
    return await service.execute_trade(trade_dict)

@router.post("/paper/order", response_model=schemas.TradeResult)
async def create_paper_order(proposal: schemas.TradeProposal) -> Any:
    """
    Submit a Paper Trading Order.
    Triggers the full Agentic Logic: User -> Market -> Strategy -> Trade -> Risk -> Execution.
    """
    from app.services.trade_service import TradeService
    
    # Convert Pydantic model to dict for internal flow
    trade_dict = proposal.model_dump()
    trade_dict["execution_mode"] = "PAPER_TRADING"
    
    # Default to Market Order if price is missing
    if not trade_dict.get("price"):
        trade_dict["price"] = 100.0 # Mock current price if not provided
        
    service = TradeService()
    return await service.execute_trade(trade_dict)


@router.post("/paper/seed-all")
def seed_paper_orders_for_traders(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    orders_per_user: int = 3,
) -> Any:
    """
    Create manual paper orders for all active traders/business owners.
    Useful for pilot dashboard/report testing.
    """
    if current_user.role not in {"SUPERADMIN", "BUSINESS_OWNER"}:
        return {"status": "forbidden", "detail": "Insufficient privileges"}

    orders_per_user = max(1, min(10, int(orders_per_user)))
    users = (
        db.query(models.user.User)
        .filter(models.user.User.is_active == True)
        .filter(models.user.User.role.in_(["TRADER", "BUSINESS_OWNER", "SUPERADMIN"]))
        .all()
    )
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC"]
    created = 0
    users_done = 0

    for user in users:
        portfolio = db.query(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == user.id).first()
        if not portfolio:
            portfolio = models.portfolio.Portfolio(
                user_id=user.id,
                name="Primary Wealth Vault",
                cash_balance=200000.0,
                invested_amount=0.0,
                win_rate=0.0,
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)

        for i in range(orders_per_user):
            symbol = random.choice(symbols)
            action = "BUY" if i % 2 == 0 else "SELL"
            price = round(random.uniform(120, 2800), 2)
            qty = random.randint(1, 15)
            pnl_val = round(random.uniform(-2.4, 3.8), 2)

            trade = models.trade.Trade(
                user_id=user.id,
                portfolio_id=portfolio.id,
                symbol=symbol,
                action=action,
                quantity=qty,
                price=price,
                status="EXECUTED",
                execution_mode="PAPER_TRADING",
                timestamp=datetime.utcnow() - timedelta(hours=(orders_per_user - i)),
                risk_score=round(random.uniform(20, 75), 2),
                pnl=f"{pnl_val}%",
                decision_logic="manual-pilot-seed",
                market_behavior="normal",
            )
            db.add(trade)
            created += 1

            if action == "BUY":
                holding = (
                    db.query(models.portfolio.Holding)
                    .filter(models.portfolio.Holding.portfolio_id == portfolio.id)
                    .filter(models.portfolio.Holding.symbol == symbol)
                    .first()
                )
                if not holding:
                    holding = models.portfolio.Holding(
                        portfolio_id=portfolio.id,
                        symbol=symbol,
                        quantity=qty,
                        avg_price=price,
                        current_price=price,
                        pnl=0.0,
                        pnl_pct=0.0,
                    )
                    db.add(holding)
                else:
                    total_qty = max(1, holding.quantity + qty)
                    holding.avg_price = round(((holding.avg_price * holding.quantity) + (price * qty)) / total_qty, 2)
                    holding.quantity = total_qty
                    holding.current_price = price
                    db.add(holding)

                portfolio.cash_balance = max(0.0, round((portfolio.cash_balance or 0) - (price * qty), 2))
                portfolio.invested_amount = round((portfolio.invested_amount or 0) + (price * qty), 2)
                db.add(portfolio)

        users_done += 1

    db.commit()
    return {"status": "ok", "users_processed": users_done, "orders_created": created}
