import React, { useState, useEffect, useMemo } from "react";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";
import { useAppData } from "../context/AppDataContext";

export function MarketTicker() {
    const { marketMovers, loading } = useAppData() || {};
    const marketStatus = (marketMovers?.status || 'UNAVAILABLE').toUpperCase();
    const marketSource = marketMovers?.source || 'none';
    const marketAsOf = marketMovers?.as_of ? new Date(marketMovers.as_of).toLocaleTimeString() : null;

    const tickerItems = useMemo(() => {
        if (!marketMovers) return [];
        const gainers = Array.isArray(marketMovers.gainers) ? marketMovers.gainers : [];
        const losers = Array.isArray(marketMovers.losers) ? marketMovers.losers : [];

        // Merge and sort slightly to mix items for a "dynamic" look
        const combined = [...gainers, ...losers];
        return combined.filter(s => s && s.symbol && s.price);
    }, [marketMovers]);

    const formatPrice = (price) => {
        const num = Number(price);
        return num.toLocaleString("en-IN", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    };

    const statusStyle = marketStatus === 'LIVE'
        ? 'bg-emerald-600/10 border-emerald-500/20 text-emerald-400'
        : marketStatus === 'STALE'
            ? 'bg-amber-500/10 border-amber-500/20 text-amber-300'
            : 'bg-rose-600/10 border-rose-500/20 text-rose-400';

    if (loading || tickerItems.length === 0) return (
        <div className="h-10 bg-[#0a0f18] border-b border-white/5 flex items-center px-4">
            <div className="flex items-center gap-2">
                <Activity size={14} className="text-blue-500 animate-pulse" />
                <span className="text-[10px] uppercase font-black tracking-widest text-slate-500">
                    {marketStatus === 'UNAVAILABLE' ? 'Market feed unavailable' : 'Connecting to Exchange Node...'}
                </span>
            </div>
        </div>
    );

    // Duplicate for seamless loop
    const displayItems = [...tickerItems, ...tickerItems, ...tickerItems];

    return (
        <div className="w-full bg-[#0a0f18] border-y border-white/5 h-10 flex items-center overflow-hidden relative shadow-2xl z-50">
            {/* Live Indicator Hook */}
            <div className="absolute left-0 top-0 bottom-0 z-10 bg-gradient-to-r from-[#0a0f18] to-transparent w-32 pointer-events-none flex items-center pl-4">
                <div className={`flex items-center gap-2 px-2 py-0.5 rounded backdrop-blur-md border ${statusStyle}`}>
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                    <span className="text-[9px] font-black tracking-tighter uppercase whitespace-nowrap">
                        {marketStatus}
                    </span>
                </div>
            </div>
            <div className="absolute right-3 top-1 z-10 text-[9px] uppercase tracking-widest text-slate-500">
                {marketSource}{marketAsOf ? ` | ${marketAsOf}` : ''}
            </div>

            <div className="ticker-wrapper flex items-center flex-nowrap animate-marquee">
                {displayItems.map((item, idx) => {
                    const change = Number(item.change_pct ?? item.change ?? 0);
                    const isUp = change >= 0;
                    return (
                        <div key={`${item.symbol}-${idx}`} className="flex items-center gap-4 px-6 border-r border-white/5 h-full whitespace-nowrap group hover:bg-white/5 transition-colors cursor-default">
                            <div className="flex flex-col">
                                <div className="flex items-center gap-1.5">
                                    <span className="text-[11px] font-black tracking-tight text-white/90 group-hover:text-blue-400 transition-colors uppercase">
                                        {item.symbol}
                                    </span>
                                    <span className="text-[8px] font-bold text-slate-500 bg-slate-800/50 px-1 rounded uppercase">
                                        {item.exchange || 'NSE'}
                                    </span>
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                <span className="text-[11px] font-bold text-slate-200 tabular-nums font-mono">
                                    ₹{formatPrice(item.price)}
                                </span>
                                <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded ${isUp ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                    {isUp ? <TrendingUp size={10} strokeWidth={3} /> : <TrendingDown size={10} strokeWidth={3} />}
                                    <span className="text-[10px] font-black tracking-tighter tabular-nums">
                                        {isUp ? '+' : ''}{change.toFixed(2)}%
                                    </span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <style>{`
                @keyframes marquee {
                    0% { transform: translateX(0); }
                    100% { transform: translateX(-33.33%); }
                }
                .animate-marquee {
                    animation: marquee 40s linear infinite;
                    will-change: transform;
                }
                .ticker-wrapper:hover {
                    animation-play-state: paused;
                }
            `}</style>
        </div>
    );
}
