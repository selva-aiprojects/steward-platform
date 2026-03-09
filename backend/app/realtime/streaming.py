from __future__ import annotations

import asyncio
import json
import logging
import os
import random
from datetime import datetime, timezone
from typing import Iterable

import socketio

from app.core.config import settings
from app.core.state import (
    clean_ticker_symbol,
    last_exchange_status,
    last_macro_indicators,
    last_market_movers,
    last_steward_prediction,
)
from app.realtime.market_provider import ProviderChain, YahooQuoteBatchProvider, YFinanceProvider

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def setup_socket(app, allowed_origins: Iterable[str]):
    socket_cors = "*" if "*" in allowed_origins else list(allowed_origins)
    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=socket_cors)
    socket_app = socketio.ASGIApp(sio, app)
    _register_socket_handlers(sio)
    return sio, socket_app


def _register_socket_handlers(sio: socketio.AsyncServer) -> None:
    @sio.event
    async def connect(sid, environ):
        print(f"Socket connected: {sid}")
        await sio.emit("connect_response", {"msg": "Connected to StockSteward AI Market Feed", "socket_id": sid}, room=sid)

    @sio.event
    async def join_stream(sid, data):
        role = (data or {}).get("role", "TRADER")
        print(f"Socket {sid} requesting stream access for role: {role}")

        if role in ["TRADER", "SUPERADMIN", "BUSINESS_OWNER"]:
            await sio.enter_room(sid, "market_data")
            await sio.emit("stream_status", {"msg": "Connected to Live Market Feed"}, to=sid)
            if last_market_movers["gainers"]:
                await sio.emit("market_movers", last_market_movers, to=sid)
            if last_steward_prediction["prediction"] != "Initializing...":
                await sio.emit("steward_prediction", last_steward_prediction, to=sid)

        if role in ["SUPERADMIN", "BUSINESS_OWNER"]:
            await sio.enter_room(sid, "admin_telemetry")
            await sio.emit("stream_status", {"msg": "Connected to Command Center Telemetry"}, to=sid)

        if role == "AUDITOR":
            await sio.enter_room(sid, "compliance_log")

    @sio.event
    async def disconnect(sid):
        print(f"Socket disconnected: {sid}")


async def market_feed(sio: socketio.AsyncServer):
    """
    Background worker that broadcasts market updates.
    """
    logging.getLogger("httpx").setLevel(logging.WARNING)

    watchlist = [
        "RELIANCE.NS",
        "TCS.NS",
        "HDFCBANK.NS",
        "INFY.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "ITC.NS",
        "LT.NS",
        "AXISBANK.NS",
        "KOTAKBANK.NS",
        "BAJFINANCE.NS",
        "MARUTI.NS",
        "^NSEI",
        "^BSESN",
        "USDINR=X",
        "EURINR=X",
        "GBPINR=X",
        "JPYINR=X",
        "AUDINR=X",
        "CADINR=X",
        "GC=F",
        "SI=F",
        "HG=F",
        "PL=F",
        "PA=F",
        "CL=F",
        "NG=F",
        "ZN=F",
    ]

    prediction_history = []
    last_ai_analysis_time = 0
    refresh_interval = 30
    failure_streak = 0
    last_heartbeat_log = 0.0
    quote_provider = ProviderChain([YahooQuoteBatchProvider(), YFinanceProvider()])

    while True:
        try:
            if not hasattr(market_feed, "groq_client"):
                groq_key = os.getenv("GROQ_API_KEY")
                if groq_key:
                    try:
                        from groq import Groq

                        market_feed.groq_client = Groq(api_key=groq_key)
                    except Exception:
                        market_feed.groq_client = None
                else:
                    market_feed.groq_client = None

            import time

            if time.time() - last_heartbeat_log > 60:
                logger.info("Market feed heartbeat: syncing live data")
                last_heartbeat_log = time.time()
            groq_client = market_feed.groq_client
            real_data_success = False
            raw_quotes = {}

            def safe_float(value):
                try:
                    if value is None:
                        return 0.0
                    return float(value)
                except Exception:
                    return 0.0

            try:
                quotes = await quote_provider.fetch_quotes(watchlist, timeout_s=6)
                if not quotes:
                    raise RuntimeError("Empty payload from quote batch API")
            except Exception as quote_error:
                raise RuntimeError(f"All market data providers failed: {quote_error}") from quote_error

            try:
                usd_inr_rate = 83.5
                if "USDINR=X" in quotes:
                    usd_inr_rate = safe_float(quotes["USDINR=X"].get("last_price", usd_inr_rate))

                for ticker_symbol in watchlist:
                    try:
                        quote = quotes.get(ticker_symbol)
                        if not quote:
                            continue

                        current_price = safe_float(quote.get("last_price"))
                        change_pct = safe_float(quote.get("change"))

                        if ticker_symbol == "GC=F":
                            current_price = (current_price / 31.1035) * usd_inr_rate * 10 * 1.15
                        elif ticker_symbol == "CL=F":
                            current_price = current_price * usd_inr_rate

                        if "^NSEI" in ticker_symbol or ".NS" in ticker_symbol:
                            exchange = "NSE"
                        elif "^BSESN" in ticker_symbol or ".BO" in ticker_symbol:
                            exchange = "BSE"
                        elif ticker_symbol.endswith("=X"):
                            exchange = "FOREX"
                        elif ticker_symbol.endswith("=F"):
                            exchange = "MCX"
                        else:
                            exchange = "NSE"

                        raw_quotes[ticker_symbol] = {
                            "last_price": safe_float(current_price),
                            "change": safe_float(change_pct),
                            "exchange": exchange,
                            "symbol": clean_ticker_symbol(ticker_symbol),
                        }
                    except Exception as ticker_err:
                        logger.debug(f"Error processing {ticker_symbol}: {ticker_err}")
                        continue

                if raw_quotes:
                    real_data_success = True
                    failure_streak = 0
                    logger.info(f"Broadcast: Real-time data sync completed for {len(raw_quotes)} instruments")
            except Exception as error:
                failure_streak += 1
                logger.warning(f"Market quote batch fetch failed: {error}")

            if real_data_success:
                quotes_list = list(raw_quotes.values())

                def to_public_quote(quote):
                    price_val = safe_float(quote.get("last_price", quote.get("price", 0)))
                    return {
                        "symbol": quote.get("symbol"),
                        "exchange": quote.get("exchange", "NSE"),
                        "last_price": round(price_val, 2),
                        "price": round(price_val, 2),
                        "change": round(safe_float(quote.get("change", 0)), 2),
                    }

                gainers_data = [
                    to_public_quote(quote)
                    for quote in sorted(
                        [quote for quote in quotes_list if quote["exchange"] in ["NSE", "BSE"]],
                        key=lambda value: value["change"],
                        reverse=True,
                    )[:10]
                ]
                losers_data = [
                    to_public_quote(quote)
                    for quote in sorted(
                        [quote for quote in quotes_list if quote["exchange"] in ["NSE", "BSE"]],
                        key=lambda value: value["change"],
                    )[:10]
                ]
                currencies = [to_public_quote(quote) for quote in quotes_list if quote["exchange"] == "FOREX"]
                metals = [
                    to_public_quote(quote)
                    for ticker_symbol, quote in raw_quotes.items()
                    if quote["exchange"] == "MCX" and ticker_symbol in ["GC=F", "SI=F", "HG=F"]
                ]
                commodities = [
                    to_public_quote(quote)
                    for ticker_symbol, quote in raw_quotes.items()
                    if quote["exchange"] == "MCX" and ticker_symbol not in ["GC=F", "SI=F", "HG=F"]
                ]

                last_macro_indicators.update(
                    {
                        "usd_inr": safe_float(usd_inr_rate),
                        "gold": safe_float(raw_quotes.get("GC=F", {}).get("last_price", 0)),
                        "crude": safe_float(raw_quotes.get("CL=F", {}).get("last_price", 0)),
                        "sentiment": "BULLISH" if len(gainers_data) > len(losers_data) else "BEARISH",
                        "volatility_level": "MODERATE",
                    }
                )

                last_market_movers.update(
                    {
                        "gainers": gainers_data,
                        "losers": losers_data,
                        "currencies": currencies,
                        "metals": metals,
                        "commodities": commodities,
                        "source": "yahoo_quote_api",
                        "status": "LIVE",
                        "as_of": _now_iso(),
                    }
                )

                await sio.emit("market_movers", last_market_movers, room="market_data")
                await sio.emit("macro_indicators", last_macro_indicators, room="market_data")
            else:
                if any(last_market_movers.get(bucket) for bucket in ["gainers", "losers", "currencies", "metals", "commodities"]):
                    last_market_movers["status"] = "STALE"
                    last_market_movers["as_of"] = last_market_movers.get("as_of") or _now_iso()
                    await sio.emit("market_movers", last_market_movers, room="market_data")
                    await sio.emit("macro_indicators", last_macro_indicators, room="market_data")
                    for bucket in ["gainers", "losers", "currencies", "metals", "commodities"]:
                        for item in last_market_movers.get(bucket, []):
                            symbol = item.get("symbol")
                            price = item.get("price", item.get("last_price"))
                            change = item.get("change", 0)
                            exchange = item.get("exchange", "NSE")
                            if not symbol or price is None:
                                continue
                            raw_quotes[symbol] = {
                                "last_price": safe_float(price),
                                "change": safe_float(change),
                                "exchange": exchange,
                                "symbol": symbol,
                            }

            ticker_batch = []
            if raw_quotes:
                for ticker_symbol, quote in raw_quotes.items():
                    ticker_batch.append(
                        {
                            "symbol": quote["symbol"],
                            "exchange": quote["exchange"],
                            "price": round(quote["last_price"], 2),
                            "change": round(quote["change"], 2),
                            "type": "up" if quote["change"] >= 0 else "down",
                        }
                    )

            if ticker_batch:
                await sio.emit("ticker_batch", ticker_batch, room="market_data")
                sample_size = min(5, len(ticker_batch))
                for update in random.sample(ticker_batch, k=sample_size):
                    await sio.emit("market_update", update, room="market_data")

            if raw_quotes:
                for ticker_symbol in watchlist:
                    if ticker_symbol in raw_quotes:
                        val = round(raw_quotes[ticker_symbol]["last_price"], 2)
                        if "USDINR" in ticker_symbol:
                            last_macro_indicators["usd_inr"] = val
                        elif "GC=F" in ticker_symbol:
                            last_macro_indicators["gold"] = val
                        elif "CL=F" in ticker_symbol:
                            last_macro_indicators["crude"] = val

            import time

            if groq_client and (time.time() - last_ai_analysis_time > 300):
                try:
                    last_ai_analysis_time = time.time()
                    market_summary = ", ".join([f"{quote['symbol']}: {quote['change']:.2f}%" for quote in ticker_batch[:5]])
                    prompt = f"Analyze market in JSON: {market_summary}"
                    completion = await asyncio.to_thread(
                        groq_client.chat.completions.create,
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"},
                        timeout=15,
                    )
                    analysis = json.loads(completion.choices[0].message.content.strip())
                    last_steward_prediction.update(
                        {
                            "prediction": analysis.get("prediction", "Market steady."),
                            "decision": analysis.get("decision", "HOLD"),
                            "confidence": analysis.get("confidence", 80),
                            "signal_mix": analysis.get("signal_mix", {"technical": 70, "fundamental": 90, "news": 50}),
                            "risk_radar": analysis.get("risk_radar", 30),
                            "history": prediction_history,
                        }
                    )
                    await sio.emit("steward_prediction", last_steward_prediction, room="market_data")
                except Exception:
                    pass

        except Exception as error:
            print(f"Market feed error: {error}")
            import traceback

            traceback.print_exc()
        finally:
            if settings.EXECUTION_MODE == "LIVE_TRADING":
                sleep_seconds = refresh_interval
            else:
                sleep_seconds = min(30, 5 + (failure_streak * 5))
            await asyncio.sleep(sleep_seconds)


async def admin_feed(sio: socketio.AsyncServer):
    while True:
        await asyncio.sleep(5)
        try:
            telemetry = {
                "active_users": random.randint(120, 500),
                "system_load": f"{random.randint(10, 45)}%",
                "latency": f"{random.randint(20, 60)}ms",
                "audit_events": random.randint(0, 5),
            }
            await sio.emit("admin_metrics", telemetry, room="admin_telemetry")
        except Exception as error:
            print(f"Admin feed error: {error}")


def start_background_tasks(sio: socketio.AsyncServer) -> None:
    if os.getenv("DISABLE_BACKGROUND_TASKS") == "1":
        return
    asyncio.create_task(market_feed(sio))
    asyncio.create_task(admin_feed(sio))
