from prometheus_client import Counter, Histogram, Gauge
from datetime import datetime, timedelta
import logging
from sqlalchemy import func
from app.core.state import last_market_movers, last_macro_indicators
from app.models.strategy import Strategy
from app.models.portfolio import Portfolio, Holding
from app.models.trade import Trade
from app.models.user import User


logger = logging.getLogger("observability.metrics")


API_REQUESTS_TOTAL = Counter(
    "stocksteward_api_requests_total",
    "Total API requests",
    ["method", "path", "status"],
)

API_REQUEST_LATENCY_SECONDS = Histogram(
    "stocksteward_api_request_latency_seconds",
    "API request latency in seconds",
    ["method", "path"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 13, 21),
)

EXTERNAL_CALLS_TOTAL = Counter(
    "stocksteward_external_calls_total",
    "External provider calls",
    ["provider", "operation", "status"],
)

EXTERNAL_CALL_LATENCY_SECONDS = Histogram(
    "stocksteward_external_call_latency_seconds",
    "External provider latency in seconds",
    ["provider", "operation"],
    buckets=(0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1, 2, 3, 5, 8, 13),
)

LLM_STRATEGY_UPDATES_TOTAL = Counter(
    "stocksteward_llm_strategy_updates_total",
    "LLM-triggered strategy updates",
    ["status"],
)

MARKET_MOVER_COUNT = Gauge(
    "stocksteward_market_mover_count",
    "Count of market movers",
    ["bucket"],
)

MARKET_MOVER_CHANGE_PCT = Gauge(
    "stocksteward_market_mover_change_pct",
    "Change percent for market movers",
    ["bucket", "symbol"],
)

MARKET_MOVER_PRICE = Gauge(
    "stocksteward_market_mover_price",
    "Last price for market movers",
    ["bucket", "symbol"],
)

MARKET_SOURCE_STATUS = Gauge(
    "stocksteward_market_source_status",
    "Market data source status (1=active)",
    ["source", "status"],
)

MACRO_INDICATOR_VALUE = Gauge(
    "stocksteward_macro_indicator",
    "Macro indicator values",
    ["name"],
)

STRATEGY_COUNT = Gauge(
    "stocksteward_strategy_count",
    "Strategies by status",
    ["status"],
)

STRATEGY_AVG_PNL_PCT = Gauge(
    "stocksteward_strategy_avg_pnl_pct",
    "Average strategy PnL percent by status",
    ["status"],
)

STRATEGY_PNL_PCT = Gauge(
    "stocksteward_strategy_pnl_pct",
    "Strategy PnL percent by strategy",
    ["strategy_id", "symbol", "status"],
)

PORTFOLIO_INVESTED_AMOUNT = Gauge(
    "stocksteward_portfolio_invested_amount",
    "Portfolio invested amount",
    ["portfolio_id", "user_id"],
)

PORTFOLIO_CASH_BALANCE = Gauge(
    "stocksteward_portfolio_cash_balance",
    "Portfolio cash balance",
    ["portfolio_id", "user_id"],
)

PORTFOLIO_WIN_RATE = Gauge(
    "stocksteward_portfolio_win_rate",
    "Portfolio win rate",
    ["portfolio_id", "user_id"],
)

HOLDING_PNL = Gauge(
    "stocksteward_holding_pnl",
    "Holding PnL (absolute)",
    ["portfolio_id", "symbol"],
)

HOLDING_PNL_PCT = Gauge(
    "stocksteward_holding_pnl_pct",
    "Holding PnL percent",
    ["portfolio_id", "symbol"],
)

TRADE_COUNT = Gauge(
    "stocksteward_trade_count",
    "Trades by status",
    ["status"],
)

TRADE_COUNT_RECENT = Gauge(
    "stocksteward_trade_count_recent",
    "Recent trades in time windows",
    ["window"],
)

USER_COUNT = Gauge(
    "stocksteward_user_count",
    "Users by role",
    ["role"],
)

PORTFOLIO_COUNT = Gauge(
    "stocksteward_portfolio_count",
    "Total portfolios",
)

HOLDING_COUNT = Gauge(
    "stocksteward_holding_count",
    "Total holdings",
)

STRATEGY_TOTAL = Gauge(
    "stocksteward_strategy_total",
    "Total strategies",
)

TRADE_TOTAL = Gauge(
    "stocksteward_trade_total",
    "Total trades",
)

TRADE_VOLUME_RECENT = Gauge(
    "stocksteward_trade_volume_recent",
    "Recent trade notional volume",
    ["window"],
)

TRADE_AVG_PRICE_RECENT = Gauge(
    "stocksteward_trade_avg_price_recent",
    "Recent average trade price",
    ["window"],
)


def record_external_call(provider: str, operation: str, latency_seconds: float | None, success: bool) -> None:
    status = "success" if success else "failure"
    EXTERNAL_CALLS_TOTAL.labels(provider=provider, operation=operation, status=status).inc()
    if latency_seconds is not None:
        EXTERNAL_CALL_LATENCY_SECONDS.labels(provider=provider, operation=operation).observe(max(latency_seconds, 0.0))


def record_strategy_update(success: bool) -> None:
    LLM_STRATEGY_UPDATES_TOTAL.labels(status="success" if success else "failure").inc()


def _parse_percent(raw: str | None) -> float | None:
    if not raw:
        return None
    value = raw.strip().replace("%", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def update_market_metrics() -> None:
    try:
        gainers = last_market_movers.get("gainers") or []
        losers = last_market_movers.get("losers") or []

        MARKET_MOVER_COUNT.labels(bucket="gainers").set(len(gainers))
        MARKET_MOVER_COUNT.labels(bucket="losers").set(len(losers))

        MARKET_MOVER_CHANGE_PCT.clear()
        MARKET_MOVER_PRICE.clear()

        for bucket, items in (("gainers", gainers), ("losers", losers)):
            for item in items[:10]:
                symbol = str(item.get("symbol") or "UNKNOWN")
                change = item.get("change")
                price = item.get("price")
                try:
                    if change is not None:
                        MARKET_MOVER_CHANGE_PCT.labels(bucket=bucket, symbol=symbol).set(float(change))
                    if price is not None:
                        MARKET_MOVER_PRICE.labels(bucket=bucket, symbol=symbol).set(float(price))
                except (TypeError, ValueError):
                    continue

        MARKET_SOURCE_STATUS.clear()
        source = str(last_market_movers.get("source") or "none")
        status = str(last_market_movers.get("status") or "UNAVAILABLE")
        MARKET_SOURCE_STATUS.labels(source=source, status=status).set(1)

        MACRO_INDICATOR_VALUE.clear()
        for key, value in (last_macro_indicators or {}).items():
            if isinstance(value, (int, float)):
                MACRO_INDICATOR_VALUE.labels(name=str(key)).set(float(value))
    except Exception as exc:
        logger.warning("Failed updating market metrics: %s", exc)


def update_strategy_metrics(db) -> None:
    try:
        strategies = db.query(Strategy).all()
        STRATEGY_PNL_PCT.clear()

        status_totals: dict[str, list[float]] = {}
        status_counts: dict[str, int] = {}
        for strategy in strategies:
            status = (strategy.status or "UNKNOWN").upper()
            status_counts[status] = status_counts.get(status, 0) + 1

            pnl_value = _parse_percent(strategy.pnl)
            if pnl_value is not None:
                status_totals.setdefault(status, []).append(pnl_value)
                STRATEGY_PNL_PCT.labels(
                    strategy_id=str(strategy.id),
                    symbol=str(strategy.symbol or "UNKNOWN"),
                    status=status,
                ).set(pnl_value)

        for status in ("RUNNING", "PAUSED", "IDLE", "UNKNOWN"):
            STRATEGY_COUNT.labels(status=status).set(status_counts.get(status, 0))
            pnl_values = status_totals.get(status, [])
            if pnl_values:
                STRATEGY_AVG_PNL_PCT.labels(status=status).set(sum(pnl_values) / len(pnl_values))
            else:
                STRATEGY_AVG_PNL_PCT.labels(status=status).set(0.0)
    except Exception as exc:
        logger.warning("Failed updating strategy metrics: %s", exc)


def update_portfolio_metrics(db) -> None:
    try:
        PORTFOLIO_COUNT.set(db.query(func.count(Portfolio.id)).scalar() or 0)
        HOLDING_COUNT.set(db.query(func.count(Holding.id)).scalar() or 0)
        PORTFOLIO_INVESTED_AMOUNT.clear()
        PORTFOLIO_CASH_BALANCE.clear()
        PORTFOLIO_WIN_RATE.clear()
        HOLDING_PNL.clear()
        HOLDING_PNL_PCT.clear()

        for portfolio in db.query(Portfolio).all():
            portfolio_id = str(portfolio.id)
            user_id = str(portfolio.user_id)
            PORTFOLIO_INVESTED_AMOUNT.labels(portfolio_id=portfolio_id, user_id=user_id).set(
                float(portfolio.invested_amount or 0.0)
            )
            PORTFOLIO_CASH_BALANCE.labels(portfolio_id=portfolio_id, user_id=user_id).set(
                float(portfolio.cash_balance or 0.0)
            )
            PORTFOLIO_WIN_RATE.labels(portfolio_id=portfolio_id, user_id=user_id).set(
                float(portfolio.win_rate or 0.0)
            )

        for holding in db.query(Holding).all():
            portfolio_id = str(holding.portfolio_id)
            symbol = str(holding.symbol or "UNKNOWN")
            HOLDING_PNL.labels(portfolio_id=portfolio_id, symbol=symbol).set(float(holding.pnl or 0.0))
            HOLDING_PNL_PCT.labels(portfolio_id=portfolio_id, symbol=symbol).set(float(holding.pnl_pct or 0.0))
    except Exception as exc:
        logger.warning("Failed updating portfolio metrics: %s", exc)


def update_trade_metrics(db) -> None:
    try:
        TRADE_TOTAL.set(db.query(func.count(Trade.id)).scalar() or 0)
        statuses = ["PENDING", "EXECUTED", "REJECTED", "FAILED"]
        for status in statuses:
            count = db.query(func.count(Trade.id)).filter(Trade.status == status).scalar() or 0
            TRADE_COUNT.labels(status=status).set(count)

        now = datetime.utcnow()
        one_hour = now - timedelta(hours=1)
        one_day = now - timedelta(days=1)

        recent_1h = db.query(func.count(Trade.id)).filter(Trade.timestamp >= one_hour).scalar() or 0
        recent_24h = db.query(func.count(Trade.id)).filter(Trade.timestamp >= one_day).scalar() or 0

        TRADE_COUNT_RECENT.labels(window="1h").set(recent_1h)
        TRADE_COUNT_RECENT.labels(window="24h").set(recent_24h)

        volume_1h = db.query(func.sum(Trade.price * Trade.quantity)).filter(Trade.timestamp >= one_hour).scalar() or 0
        volume_24h = db.query(func.sum(Trade.price * Trade.quantity)).filter(Trade.timestamp >= one_day).scalar() or 0
        TRADE_VOLUME_RECENT.labels(window="1h").set(float(volume_1h or 0))
        TRADE_VOLUME_RECENT.labels(window="24h").set(float(volume_24h or 0))

        avg_price_1h = db.query(func.avg(Trade.price)).filter(Trade.timestamp >= one_hour).scalar() or 0
        avg_price_24h = db.query(func.avg(Trade.price)).filter(Trade.timestamp >= one_day).scalar() or 0
        TRADE_AVG_PRICE_RECENT.labels(window="1h").set(float(avg_price_1h or 0))
        TRADE_AVG_PRICE_RECENT.labels(window="24h").set(float(avg_price_24h or 0))
    except Exception as exc:
        logger.warning("Failed updating trade metrics: %s", exc)


def update_user_metrics(db) -> None:
    try:
        roles = ["SUPERADMIN", "BUSINESS_OWNER", "TRADER", "AUDITOR"]
        for role in roles:
            count = db.query(func.count(User.id)).filter(User.role == role).scalar() or 0
            USER_COUNT.labels(role=role).set(count)
        STRATEGY_TOTAL.set(db.query(func.count(Strategy.id)).scalar() or 0)
    except Exception as exc:
        logger.warning("Failed updating user metrics: %s", exc)
