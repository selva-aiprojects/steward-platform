from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import httpx


class MarketDataProvider(ABC):
    @abstractmethod
    async def fetch_quotes(self, symbols: List[str], timeout_s: int = 6) -> Dict[str, Dict[str, float]]:
        raise NotImplementedError


class YahooQuoteBatchProvider(MarketDataProvider):
    async def fetch_quotes(self, symbols: List[str], timeout_s: int = 6) -> Dict[str, Dict[str, float]]:
        timeout = httpx.Timeout(timeout_s)
        headers = {"User-Agent": "Mozilla/5.0"}
        quotes: Dict[str, Dict[str, float]] = {}
        semaphore = asyncio.Semaphore(8)

        async def fetch_one(client: httpx.AsyncClient, symbol: str) -> Tuple[str, Optional[Dict[str, float]]]:
            async with semaphore:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                response = await client.get(url, params={"range": "5d", "interval": "1d"})
                response.raise_for_status()
                payload = response.json() or {}
                result = ((payload.get("chart") or {}).get("result") or [None])[0]
                if not result:
                    return symbol, None
                closes = ((((result.get("indicators") or {}).get("quote") or [{}])[0]).get("close") or [])
                values = []
                for value in closes:
                    if value is None:
                        continue
                    try:
                        values.append(float(value))
                    except Exception:
                        continue
                if not values:
                    return symbol, None
                current_f = values[-1]
                prev_f = values[-2] if len(values) > 1 else current_f
                change = 0.0 if prev_f == 0 else ((current_f - prev_f) / prev_f) * 100
                return symbol, {"last_price": current_f, "change": change}

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            results = await asyncio.gather(*(fetch_one(client, symbol) for symbol in symbols), return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                continue
            symbol, payload = result
            if payload:
                quotes[symbol] = payload
        return quotes


class YFinanceProvider(MarketDataProvider):
    async def fetch_quotes(self, symbols: List[str], timeout_s: int = 10) -> Dict[str, Dict[str, float]]:
        import pandas as pd
        import yfinance as yf

        quotes: Dict[str, Dict[str, float]] = {}
        data = await asyncio.wait_for(
            asyncio.to_thread(
                yf.download,
                symbols,
                period="5d",
                group_by="ticker",
                progress=False,
                auto_adjust=False,
                timeout=8,
                threads=False,
            ),
            timeout=timeout_s,
        )

        for ticker_symbol in symbols:
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    if ticker_symbol not in data.columns.levels[0]:
                        continue
                    ticker_df = data[ticker_symbol].dropna(subset=["Close"])
                else:
                    ticker_df = data.dropna(subset=["Close"])
                if ticker_df.empty:
                    continue
                current_price = float(ticker_df["Close"].iloc[-1])
                prev_price = float(ticker_df["Close"].iloc[-2]) if len(ticker_df) > 1 else current_price
                change_pct = 0.0 if prev_price == 0 else ((current_price - prev_price) / prev_price * 100)
                quotes[ticker_symbol] = {"last_price": current_price, "change": change_pct}
            except Exception:
                continue
        return quotes


class KiteProvider(MarketDataProvider):
    async def fetch_quotes(self, symbols: List[str], timeout_s: int = 6) -> Dict[str, Dict[str, float]]:
        # Placeholder provider. Wire Zerodha quote APIs here once symbol mapping is finalized.
        return {}


class TrueDataProvider(MarketDataProvider):
    async def fetch_quotes(self, symbols: List[str], timeout_s: int = 6) -> Dict[str, Dict[str, float]]:
        # Placeholder provider. Wire TrueData APIs here when credentials/contract are available.
        return {}


class ProviderChain(MarketDataProvider):
    def __init__(self, providers: List[MarketDataProvider]):
        self.providers = providers

    async def fetch_quotes(self, symbols: List[str], timeout_s: int = 6) -> Dict[str, Dict[str, float]]:
        last_error: Optional[Exception] = None
        for provider in self.providers:
            try:
                quotes = await provider.fetch_quotes(symbols, timeout_s=timeout_s)
                if quotes:
                    return quotes
            except Exception as error:
                last_error = error
                continue
        if last_error:
            raise RuntimeError(str(last_error))
        return {}
