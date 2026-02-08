import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { useAppData } from '../context/AppDataContext';

// Example NSE/BSE wrapper (adjust/remove if you use your own backend)[web:1]
const API_BASE = 'http://nse-api-khaki.vercel.app:5000';

const POLL_INTERVAL = 15000; // 15 seconds

// Symbols
const NSE_SYMBOL   = 'RELIANCE';   // NSE
const BSE_SYMBOL   = '^BSESN';     // Sensex index on Yahoo[web:12]
const MCX_SYMBOL   = 'CRUDEOIL';   // Crude proxy (CL=F on Yahoo)
const FX_SYMBOL    = 'USD';        // For INR→USD via exchangerate.host[web:30][web:37]

export function MarketTicker() {
    const [tickers, setTickers] = useState({
        NSE:   { symbol: 'RELIANCE', exchange: 'NSE',    price: null, change: 0, changePct: 0 },
        BSE:   { symbol: 'SENSEX',   exchange: 'BSE',    price: null, change: 0, changePct: 0 },
        MCX:   { symbol: 'CRUDEOIL', exchange: 'MCX',    price: null, change: 0, changePct: 0 },
        FX:    { symbol: 'USDINR',   exchange: 'FX',     price: null, change: 0, changePct: 0 },
        METAL: { symbol: 'GOLD',     exchange: 'METAL',  price: null, change: 0, changePct: 0 }
    });

    const { marketMovers, watchlist } = useAppData();

    const fetchTicker = useCallback(async (symbol, exchange) => {
        try {
            let url;

            if (exchange === 'FX') {
                // 1 INR → USD; we invert to display USDINR (INR per 1 USD)[web:30][web:37]
                url = 'https://api.exchangerate.host/latest?base=INR&symbols=USD';
            } else if (exchange === 'METAL') {
                // FreeGoldAPI: latest gold price, no API key, JSON array[web:43]
                url = 'https://freegoldapi.com/data/latest.json';
            } else if (exchange === 'MCX') {
                // Crude Oil via Yahoo (CL=F)
                url = 'https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=1d&interval=1m';
            } else if (exchange === 'BSE' && symbol === '^BSESN') {
                // Sensex via Yahoo[web:12]
                url = 'https://query1.finance.yahoo.com/v8/finance/chart/^BSESN?range=1d&interval=5m';
            } else {
                // NSE/BSE via your proxy / free API[web:1]
                const suffix = exchange === 'BSE' ? '.BO' : '.NS';
                url = `${API_BASE}/stock?symbol=${symbol}${suffix}&res=num`;
            }

            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            let price = null;
            let change = 0;
            let changePct = 0;

            if (exchange === 'FX') {
                const rate = data?.rates?.USD;
                if (rate) {
                    // 1 INR = rate USD → USDINR = 1 / rate
                    price = 1 / rate;
                }
            } else if (exchange === 'METAL') {
                // data is an array; last element is latest[web:43]
                const latest = Array.isArray(data) && data.length ? data[data.length - 1] : null;
                if (latest?.price) {
                    // Price is in USD; for demo just show USD value as-is
                    price = latest.price;
                }
            } else if (exchange === 'MCX') {
                const meta = data?.chart?.result?.[0]?.meta;
                if (meta) {
                    price = meta.regularMarketPrice;
                    change = meta.regularMarketChange;
                    changePct = meta.regularMarketChangePercent;
                }
            } else if (exchange === 'BSE' && symbol === '^BSESN') {
                const meta = data?.chart?.result?.[0]?.meta;
                if (meta) {
                    price = meta.regularMarketPrice;
                    change = meta.regularMarketChange;
                    changePct = meta.regularMarketChangePercent;
                }
            } else {
                if (data.status === 'success' && data.data) {
                    price = data.data.last_price;
                    change = data.data.change;
                    changePct = data.data.percent_change;
                }
            }

            return {
                price: price ?? null,
                change: Number(change) || 0,
                changePct: Number(changePct) || 0
            };
        } catch (err) {
            console.error(`Fetch error for ${exchange} ${symbol}:`, err);
            return { price: null, change: 0, changePct: 0 };
        }
    }, []);

    const updateAllTickers = useCallback(async () => {
        const [nse, bse, mcx, fx, metal] = await Promise.all([
            fetchTicker(NSE_SYMBOL, 'NSE'),
            fetchTicker(BSE_SYMBOL, 'BSE'),
            fetchTicker(MCX_SYMBOL, 'MCX'),
            fetchTicker(FX_SYMBOL, 'FX'),
            fetchTicker('GOLD', 'METAL')
        ]);

        setTickers(prev => ({
            NSE:   { ...prev.NSE,   ...nse },
            BSE:   { ...prev.BSE,   ...bse },
            MCX:   { ...prev.MCX,   ...mcx },
            FX:    { ...prev.FX,    ...fx },
            METAL: { ...prev.METAL, ...metal }
        }));
    }, [fetchTicker]);

    useEffect(() => {
        updateAllTickers();
        const interval = setInterval(updateAllTickers, POLL_INTERVAL);
        return () => clearInterval(interval);
    }, [updateAllTickers]);

    // Optional: fallback from context if any price is still null
    useEffect(() => {
        if (!Array.isArray(marketMovers) && !Array.isArray(watchlist)) return;

        setTickers(prev => {
            const updated = { ...prev };

            const all = [
                ...(Array.isArray(marketMovers) ? marketMovers : []),
                ...(Array.isArray(watchlist) ? watchlist : [])
            ];

            const mapFallback = (symbol, key) => {
                const found = all.find(i => i.symbol === symbol);
                if (found && updated[key].price == null) {
                    updated[key] = {
                        ...updated[key],
                        price: found.price || found.last_price || found.current_price || updated[key].price,
                        change: found.change || found.change_abs || updated[key].change,
                        changePct: found.change_pct || found.percent_change || updated[key].changePct
                    };
                }
            };

            mapFallback('RELIANCE', 'NSE');
            mapFallback('SENSEX', 'BSE');
            mapFallback('CRUDEOIL', 'MCX');

            return updated;
        });
    }, [marketMovers, watchlist]);

    const exchangeClass = (exchange) => {
        switch (exchange) {
            case 'NSE':
                return 'text-emerald-300 border-emerald-500/60';
            case 'BSE':
                return 'text-sky-300 border-sky-500/60';
            case 'MCX':
                return 'text-amber-300 border-amber-500/60';
            case 'FX':
                return 'text-fuchsia-300 border-fuchsia-500/60';
            case 'METAL':
                return 'text-yellow-300 border-yellow-500/60';
            default:
                return 'text-slate-300 border-slate-500/60';
        }
    };

    const formatPrice = (value, exchange) => {
        if (value === null || value === 0) return '--';

        const decimals =
            exchange === 'FX' || exchange === 'METAL'
                ? 4
                : 2;

        // For demo, still prefix with INR; you can switch to USD for metals explicitly
        return `INR ${Number(value).toLocaleString('en-IN', {
            maximumFractionDigits: decimals
        })}`;
    };

    const lines = [
        { key: 'NSE',   data: tickers.NSE },
        { key: 'BSE',   data: tickers.BSE },
        { key: 'MCX',   data: tickers.MCX },
        { key: 'FX',    data: tickers.FX },
        { key: 'METAL', data: tickers.METAL }
    ];

    return (
        <div className="w-full bg-slate-900 border-b border-slate-800 py-2 overflow-hidden relative h-28 flex flex-col justify-center">
            {lines.map(({ key, data }) => (
                <div
                    key={key}
                    className="flex animate-marquee whitespace-nowrap gap-8 pr-12 mb-1 last:mb-0"
                >
                    <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm min-w-0">
                        <div className="flex flex-col min-w-0">
              <span
                  className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(
                      data.exchange
                  )} truncate`}
              >
                {data.exchange}
              </span>
                            <span className="text-[11px] font-black text-white uppercase tracking-tight truncate max-w-[100px]">
                {data.symbol}
              </span>
                        </div>
                        <div className="flex flex-col items-end flex-1">
              <span className="text-[11px] font-black text-white">
                {formatPrice(data.price, data.exchange)}
              </span>
                            <div
                                className={`flex items-center gap-0.5 text-[9px] font-bold ${
                                    data.changePct >= 0 ? 'text-green-300' : 'text-red-300'
                                }`}
                            >
                                {data.changePct >= 0 ? (
                                    <TrendingUp size={8} />
                                ) : (
                                    <TrendingDown size={8} />
                                )}
                                {data.changePct >= 0 ? '+' : ''}
                                {(data.changePct || 0).toFixed(2)}%
                            </div>
                        </div>
                    </div>
                </div>
            ))}

            {/* Left LIVE badge */}
            <div className="absolute left-0 top-0 h-full bg-slate-900 px-4 flex items-center border-r border-slate-800 z-10 shadow-2xl">
                <div className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#10b981]" />
                    <span className="text-[8px] font-black text-white uppercase tracking-[0.2em]">
            Market Watch
          </span>
                </div>
            </div>
        </div>
    );
}
