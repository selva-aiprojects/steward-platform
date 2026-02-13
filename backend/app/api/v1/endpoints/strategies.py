from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Dict
import os
import random
from datetime import datetime, timedelta
from app import schemas, models
from app.core.database import get_db
from app.core.rbac import get_current_user

router = APIRouter()


def _bootstrap_pilot_progress(
    db: Session,
    user_id: int,
    strategy: models.strategy.Strategy,
    portfolio: models.portfolio.Portfolio,
) -> Dict[str, Any]:
    """
    Seed minimal paper progress so pilot users can immediately see strategy movement.
    Idempotent by user: if user already has holdings or trades, no data is injected.
    """
    holdings_count = db.query(models.portfolio.Holding).filter(models.portfolio.Holding.portfolio_id == portfolio.id).count()
    trades_count = db.query(models.trade.Trade).filter(models.trade.Trade.portfolio_id == portfolio.id).count()
    if holdings_count > 0 or trades_count > 0:
        return {"seeded": False, "reason": "existing_activity"}

    base_capital = 250000.0
    entry_price = round(random.uniform(900, 2200), 2)
    quantity = random.randint(10, 40)
    invested = round(entry_price * quantity, 2)
    last_price = round(entry_price * random.uniform(0.98, 1.06), 2)
    pnl_abs = round((last_price - entry_price) * quantity, 2)
    pnl_pct = round((pnl_abs / invested) * 100 if invested else 0, 2)

    holding = models.portfolio.Holding(
        portfolio_id=portfolio.id,
        symbol=(strategy.symbol or "RELIANCE").upper(),
        quantity=quantity,
        avg_price=entry_price,
        current_price=last_price,
        pnl=pnl_abs,
        pnl_pct=pnl_pct,
    )
    db.add(holding)

    # Backfill a few paper trades to populate reports/history views.
    now = datetime.utcnow()
    trade_rows = []
    for idx in range(5):
        action = "BUY" if idx % 2 == 0 else "SELL"
        trade_price = round(entry_price * random.uniform(0.97, 1.04), 2)
        trade_qty = max(1, quantity // random.randint(2, 5))
        trade_rows.append(
            models.trade.Trade(
                user_id=user_id,
                portfolio_id=portfolio.id,
                symbol=(strategy.symbol or "RELIANCE").upper(),
                action=action,
                quantity=trade_qty,
                price=trade_price,
                status="EXECUTED",
                execution_mode="PAPER_TRADING",
                timestamp=now - timedelta(days=(5 - idx)),
                risk_score=round(random.uniform(22, 68), 2),
                pnl=f"{round(random.uniform(-2.2, 3.5), 2)}%",
                decision_logic="pilot-seeded-momentum",
                market_behavior="normal",
            )
        )
    db.add_all(trade_rows)

    portfolio.name = portfolio.name or "Primary Wealth Vault"
    portfolio.invested_amount = invested
    portfolio.cash_balance = max(0.0, round(base_capital - invested, 2))
    portfolio.win_rate = round(random.uniform(53, 71), 2)

    strategy.status = strategy.status or "RUNNING"
    strategy.pnl = f"{'+' if pnl_pct >= 0 else ''}{pnl_pct}%"
    strategy.execution_mode = "PAPER_TRADING"

    db.add(portfolio)
    db.add(strategy)
    db.commit()
    return {"seeded": True, "holding_symbol": holding.symbol, "trades": len(trade_rows)}

@router.get("/", response_model=List[schemas.strategy.StrategyResponse])
def read_strategies(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    query = db.query(models.strategy.Strategy)

    # Allow users to only see their own strategies unless they're an admin
    if user_id:
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to view strategies for this user")
        query = query.join(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == user_id)
    else:
        # Default to current user's strategies
        query = query.join(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == current_user.id)

    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.strategy.StrategyResponse)
def create_strategy(
    strategy: schemas.strategy.StrategyLaunchRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Launch a new strategy using user_id.
    Maps user_id to portfolio_id for frontend compatibility.
    """
    # Ensure the user can only create strategies for themselves
    if strategy.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to create strategy for this user")

    portfolio = db.query(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == strategy.user_id).first()
    if not portfolio:
        # Auto-create portfolio if not exists for demo robustness
        portfolio = models.portfolio.Portfolio(user_id=strategy.user_id, name="Auto-Created Portfolio")
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    strat_data = {
        "portfolio_id": portfolio.id,
        "name": strategy.name,
        "symbol": strategy.symbol,
        "status": strategy.status,
        "pnl": strategy.pnl,
        "drawdown": strategy.drawdown,
        "execution_mode": strategy.execution_mode
    }

    db_strategy = models.strategy.Strategy(**strat_data)
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)

    auto_seed = os.getenv("PILOT_AUTO_SEED_PROGRESS", "1").strip() == "1"
    if auto_seed:
        _bootstrap_pilot_progress(db, strategy.user_id, db_strategy, portfolio)
        db.refresh(db_strategy)

    return db_strategy


@router.post("/pilot/bootstrap")
def bootstrap_pilot_users(
    *,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_id: int | None = None,
) -> Any:
    """
    Backfill pilot progress for existing users so dashboard/progress views are non-empty.
    SUPERADMIN/BUSINESS_OWNER only.
    """
    if current_user.role not in {"SUPERADMIN", "BUSINESS_OWNER"}:
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    users_query = db.query(models.user.User).filter(models.user.User.is_active == True)
    if user_id:
        users_query = users_query.filter(models.user.User.id == user_id)
    users = users_query.all()

    results = []
    for user in users:
        if user.role in {"AUDITOR"}:
            continue
        portfolio = db.query(models.portfolio.Portfolio).filter(models.portfolio.Portfolio.user_id == user.id).first()
        if not portfolio:
            portfolio = models.portfolio.Portfolio(user_id=user.id, name="Primary Wealth Vault")
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)

        strat = (
            db.query(models.strategy.Strategy)
            .filter(models.strategy.Strategy.portfolio_id == portfolio.id)
            .order_by(models.strategy.Strategy.id.desc())
            .first()
        )
        if not strat:
            strat = models.strategy.Strategy(
                portfolio_id=portfolio.id,
                name="Pilot Momentum Alpha",
                symbol="RELIANCE",
                status="RUNNING",
                pnl="0%",
                drawdown=0.0,
                execution_mode="PAPER_TRADING",
            )
            db.add(strat)
            db.commit()
            db.refresh(strat)

        seed = _bootstrap_pilot_progress(db, user.id, strat, portfolio)
        results.append({
            "user_id": user.id,
            "email": user.email,
            "strategy_id": strat.id,
            **seed,
        })

    return {"status": "ok", "count": len(results), "results": results}
