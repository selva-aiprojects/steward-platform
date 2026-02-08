import React, { useState, useEffect, useMemo } from 'react';
import { TrendingUp, TrendingDown, Zap } from 'lucide-react';
import { socket, fetchMarketMovers } from '../services/api';
import { useAppData } from '../context/AppDataContext';

export function MarketTicker() {
    const [stocks, setStocks] = useState([]);
    const { marketMovers, watchlist } = useAppData();
    const maxItems = 60;
    const fallbackStocks = [
        { symbol: 'RELIANCE', exchange: 'NSE', price: 2987.5, change: 1.2 },
        { symbol: 'SENSEX', exchange: 'BSE', price: 72150, change: 0.6 },
        { symbol: 'CRUDEOIL', exchange: 'MCX', price: 6985, change: -0.4 }
    ];
    const fallbackUniverse = useMemo(() => ([
        { symbol: 'RELIANCE', exchange: 'NSE' },
        { symbol: 'TCS', exchange: 'NSE' },
        { symbol: 'HDFCBANK', exchange: 'NSE' },
        { symbol: 'INFY', exchange: 'NSE' },
        { symbol: 'ICICIBANK', exchange: 'NSE' },
        { symbol: 'SBIN', exchange: 'NSE' },
        { symbol: 'ITC', exchange: 'NSE' },
        { symbol: 'LT', exchange: 'NSE' },
        { symbol: 'AXISBANK', exchange: 'NSE' },
        { symbol: 'KOTAKBANK', exchange: 'NSE' },
        { symbol: 'BAJFINANCE', exchange: 'NSE' },
        { symbol: 'BAJAJFINSV', exchange: 'NSE' },
        { symbol: 'MARUTI', exchange: 'NSE' },
        { symbol: 'TATAMOTORS', exchange: 'NSE' },
        { symbol: 'BHARTIARTL', exchange: 'NSE' },
        { symbol: 'ADANIENT', exchange: 'NSE' },
        { symbol: 'ADANIPORTS', exchange: 'NSE' },
        { symbol: 'ASIANPAINT', exchange: 'NSE' },
        { symbol: 'ULTRACEMCO', exchange: 'NSE' },
        { symbol: 'WIPRO', exchange: 'NSE' },
        { symbol: 'TECHM', exchange: 'NSE' },
        { symbol: 'HCLTECH', exchange: 'NSE' },
        { symbol: 'ONGC', exchange: 'NSE' },
        { symbol: 'POWERGRID', exchange: 'NSE' },
        { symbol: 'NTPC', exchange: 'NSE' },
        { symbol: 'COALINDIA', exchange: 'NSE' },
        { symbol: 'SUNPHARMA', exchange: 'NSE' },
        { symbol: 'DRREDDY', exchange: 'NSE' },
        { symbol: 'CIPLA', exchange: 'NSE' },
        { symbol: 'HINDUNILVR', exchange: 'NSE' },
        { symbol: 'SENSEX', exchange: 'BSE' },
        { symbol: 'BOM500002', exchange: 'BSE' },
        { symbol: 'BOM500010', exchange: 'BSE' },
        { symbol: 'GOLD', exchange: 'MCX' },
        { symbol: 'SILVER', exchange: 'MCX' },
        { symbol: 'CRUDEOIL', exchange: 'MCX' },
        { symbol: 'NATURALGAS', exchange: 'MCX' }
    ]), []);
    const exchangeClass = (exchange) => {
        switch ((exchange || '').toUpperCase()) {
            case 'NSE':
                return 'text-emerald-300 border-emerald-500/60';
            case 'BSE':
                return 'text-sky-300 border-sky-500/60';
            case 'MCX':
                return 'text-amber-300 border-amber-500/60';
            default:
                return 'text-slate-300 border-slate-500/60';
        }
    };
    const formatPrice = (value) => {
        if (value === null || value === undefined) return 'INR --';
        const num = typeof value === 'number' ? value : parseFloat(value);
        if (!Number.isFinite(num) || num === 0) return 'INR --';
        return `INR ${num.toLocaleString()}`;
    };

    useEffect(() => {
        const handleUpdate = (data) => {
            setStocks(prev => {
                const key = `${data.exchange || 'NSE'}:${data.symbol}`;
                const exists = prev.find(s => `${s.exchange || 'NSE'}:${s.symbol}` === key);
                if (exists) {
                    return prev.map(s => `${s.exchange || 'NSE'}:${s.symbol}` === key ? { ...s, ...data } : s);
                }
                if (prev.length >= maxItems) return prev;
                return [...prev, data];
            });
        };

        socket.on('market_update', handleUpdate);
        return () => socket.off('market_update', handleUpdate);
    }, []);

    useEffect(() => {
        if (stocks.length > 0) return;

        const fromMovers = (Array.isArray(marketMovers) ? marketMovers : [])
            .map(m => ({
                symbol: m.symbol,
                exchange: m.exchange || 'NSE',
                price: m.price || m.last_price || 0,
                change: m.change || 0
            }));

        const fromWatchlist = (Array.isArray(watchlist) ? watchlist : [])
            .map(w => ({
                symbol: w.symbol,
                exchange: w.exchange || 'NSE',
                price: w.price || w.current_price || w.last_price || 0,
                change: w.change || w.change_pct || 0
            }));

        const fromUniverse = fallbackUniverse.map(item => ({
            ...item,
            price: 0,
            change: 0
        }));

        const combined = [...fromMovers, ...fromWatchlist, ...fromUniverse];
        const seen = new Set();
        const seed = combined.filter(item => {
            if (!item.symbol) return false;
            const key = `${item.exchange || 'NSE'}:${item.symbol}`;
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
        }).slice(0, maxItems);

        if (seed.length > 0) {
            setStocks(seed);
        }
    }, [marketMovers, watchlist, fallbackUniverse, stocks.length]);

    useEffect(() => {
        const poll = async () => {
            if (stocks.length >= maxItems) return;
            const data = await fetchMarketMovers();
            if (data?.gainers) {
                const seed = [...data.gainers, ...data.losers].map(m => ({
                    symbol: m.symbol,
                    exchange: m.exchange || 'NSE',
                    price: m.price || m.last_price || 0,
                    change: m.change || 0
                }));
                if (seed.length) {
                    setStocks(seed.slice(0, maxItems));
                }
            }
        };
        const interval = setInterval(poll, 5000);
        poll();
        const fallbackTimer = setTimeout(() => {
            if (stocks.length === 0) {
                setStocks(fallbackStocks);
            }
        }, 2500);
        return () => {
            clearInterval(interval);
            clearTimeout(fallbackTimer);
        };
    }, [stocks.length]);

    if (stocks.length === 0) return null;

    // Group stocks by exchange and take only the first one for each exchange
    const groupedStocks = useMemo(() => {
        const groups = {
            'NSE': [],
            'BSE': [],
            'MCX': []
        };

        stocks.forEach(stock => {
            const exchange = stock.exchange || 'NSE';
            if (groups[exchange.toUpperCase()]) {
                groups[exchange.toUpperCase()].push(stock);
            }
        });

        // Take the first stock from each exchange group
        return [
            groups.NSE[0] || { symbol: 'RELIANCE', exchange: 'NSE', price: 0, change: 0 },
            groups.BSE[0] || { symbol: 'SENSEX', exchange: 'BSE', price: 0, change: 0 },
            groups.MCX[0] || { symbol: 'CRUDEOIL', exchange: 'MCX', price: 0, change: 0 }
        ].filter(stock => stock); // Filter out any undefined values
    }, [stocks]);

    return (
        <div className="w-full bg-slate-900 border-b border-slate-800 py-2 overflow-hidden relative h-16 flex flex-col justify-center"> {/* Increased height to accommodate 3 lines */}
            {/* NSE Line */}
            {groupedStocks[0] && (
                <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12 mb-1">
                    <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                        <div className="flex flex-col">
                            <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(groupedStocks[0].exchange)}`}>
                                {groupedStocks[0].exchange || 'NSE'}
                            </span>
                            <span className="text-[11px] font-black text-white uppercase tracking-tight">{groupedStocks[0].symbol}</span>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="text-[11px] font-black text-white">{formatPrice(groupedStocks[0].price)}</span>
                            <div className={`flex items-center gap-0.5 text-[9px] font-bold ${parseFloat(groupedStocks[0].change) >= 0 ? 'text-green-300' : 'text-red-300'
                                }`}>
                                {parseFloat(groupedStocks[0].change) >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                                {parseFloat(groupedStocks[0].change) >= 0 ? '+' : ''}{groupedStocks[0].change}%
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* BSE Line */}
            {groupedStocks[1] && (
                <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12 mb-1">
                    <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                        <div className="flex flex-col">
                            <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(groupedStocks[1].exchange)}`}>
                                {groupedStocks[1].exchange || 'BSE'}
                            </span>
                            <span className="text-[11px] font-black text-white uppercase tracking-tight">{groupedStocks[1].symbol}</span>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="text-[11px] font-black text-white">{formatPrice(groupedStocks[1].price)}</span>
                            <div className={`flex items-center gap-0.5 text-[9px] font-bold ${parseFloat(groupedStocks[1].change) >= 0 ? 'text-green-300' : 'text-red-300'
                                }`}>
                                {parseFloat(groupedStocks[1].change) >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                                {parseFloat(groupedStocks[1].change) >= 0 ? '+' : ''}{groupedStocks[1].change}%
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* MCX Line */}
            {groupedStocks[2] && (
                <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12">
                    <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                        <div className="flex flex-col">
                            <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(groupedStocks[2].exchange)}`}>
                                {groupedStocks[2].exchange || 'MCX'}
                            </span>
                            <span className="text-[11px] font-black text-white uppercase tracking-tight">{groupedStocks[2].symbol}</span>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="text-[11px] font-black text-white">{formatPrice(groupedStocks[2].price)}</span>
                            <div className={`flex items-center gap-0.5 text-[9px] font-bold ${parseFloat(groupedStocks[2].change) >= 0 ? 'text-green-300' : 'text-red-300'
                                }`}>
                                {parseFloat(groupedStocks[2].change) >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                                {parseFloat(groupedStocks[2].change) >= 0 ? '+' : ''}{groupedStocks[2].change}%
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Overlay for "Live" indicator */}
            <div className="absolute left-0 top-0 h-full bg-slate-900 px-4 flex items-center border-r border-slate-800 z-10 shadow-2xl">
                <div className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse shadow-[0_0_8px_#2DBD42]" />
                    <span className="text-[8px] font-black text-white uppercase tracking-[0.2em]">Market Watch</span>
                </div>
            </div>
        </div>
    );
}


