from fastapi import APIRouter, Depends, HTTPException, Header, Request
from typing import Dict, Any, List, Optional
from app import schemas
import random
from datetime import datetime, timedelta

router = APIRouter()

from sqlalchemy.orm import Session
from app.core.database import get_db
from app import models
from app.core.rbac import get_current_user
from app.core.config import settings
from app.core.idempotency import idempotency_store
from app.core.rate_limit import rate_limiter
from app.application.trade_application_service import TradeApplicationService

trade_app_service = TradeApplicationService()

@router.get("/", response_model=List[schemas.TradeResponse])
def list_trades(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve trades.
    """
    try:
        return trade_app_service.list_trades(
            db=db,
            actor_user=current_user,
            requested_user_id=user_id,
            skip=skip,
            limit=limit,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

@router.post("/", response_model=schemas.TradeResult)
async def execute_trade_endpoint(
    proposal: schemas.TradeProposal,
    request: Request,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """
    Execute a trade. 
    This is the standard endpoint hit by the frontend 'executeTrade' service.
    """
    trade_dict = proposal.model_dump()
    try:
        client_host = request.client.host if request.client else "unknown"
        rate_key = f"trade:{current_user.id}:{client_host}"
        if not rate_limiter.allow(
            key=rate_key,
            limit=settings.TRADE_RATE_LIMIT_PER_MINUTE,
            window_seconds=60,
        ):
            raise HTTPException(status_code=429, detail="Trade rate limit exceeded")

        cache_key = None
        if idempotency_key:
            cache_key = f"{current_user.id}:{idempotency_key}:execute"
            cached = idempotency_store.get(cache_key)
            if cached is not None:
                return cached

        result = await trade_app_service.submit_order(
            db=db,
            actor_user=current_user,
            proposal=trade_dict,
        )
        if cache_key:
            idempotency_store.put(cache_key, result, settings.IDEMPOTENCY_TTL_SECONDS)
        return result
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post("/paper/order", response_model=schemas.TradeResult)
async def create_paper_order(
    proposal: schemas.TradeProposal,
    request: Request,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """
    Submit a Paper Trading Order.
    Triggers the full Agentic Logic: User -> Market -> Strategy -> Trade -> Risk -> Execution.
    """
    trade_dict = proposal.model_dump()
    try:
        client_host = request.client.host if request.client else "unknown"
        rate_key = f"trade-paper:{current_user.id}:{client_host}"
        if not rate_limiter.allow(
            key=rate_key,
            limit=settings.TRADE_RATE_LIMIT_PER_MINUTE,
            window_seconds=60,
        ):
            raise HTTPException(status_code=429, detail="Trade rate limit exceeded")

        cache_key = None
        if idempotency_key:
            cache_key = f"{current_user.id}:{idempotency_key}:paper"
            cached = idempotency_store.get(cache_key)
            if cached is not None:
                return cached

        result = await trade_app_service.submit_order(
            db=db,
            actor_user=current_user,
            proposal=trade_dict,
            force_execution_mode="PAPER_TRADING",
        )
        if cache_key:
            idempotency_store.put(cache_key, result, settings.IDEMPOTENCY_TTL_SECONDS)
        return result
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
@router.get("/daily-pnl", response_model=List[Dict[str, Any]])
def get_daily_pnl(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    user_id: Optional[int] = None,
) -> Any:
    """
    Get daily PnL summary for a user.
    """
    try:
        return trade_app_service.get_daily_pnl(
            db=db,
            actor_user=current_user,
            requested_user_id=user_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
