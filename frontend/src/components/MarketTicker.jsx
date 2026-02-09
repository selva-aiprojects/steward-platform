import React, { useState, useEffect, useMemo } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { useAppData } from '../context/AppDataContext';

export function MarketTicker() {
    const { marketMovers, loading } = useAppData();
    
    // Define fallback stocks for each exchange
    const fallbackStocks = useMemo(() => [
        { symbol: 'RELIANCE', exchange: 'NSE', price: 2987.5, change: 1.2 },
        { symbol: 'HDFCBANK', exchange: 'NSE', price: 1450, change: 0.8 },
        { symbol: 'INFY', exchange: 'NSE', price: 1540, change: 0.6 },
        { symbol: 'SENSEX', exchange: 'BSE', price: 72150, change: 0.6 },
        { symbol: 'BOM500002', exchange: 'BSE', price: 17900, change: 0.4 },
        { symbol: 'CRUDEOIL', exchange: 'MCX', price: 6985, change: -0.4 },
        { symbol: 'GOLD', exchange: 'MCX', price: 62450, change: 0.7 },
        { symbol: 'SILVER', exchange: 'MCX', price: 74200, change: -0.2 }
    ], []);

    // Exchange-specific styling
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

    // Format price with proper currency
    const formatPrice = (value) => {
        if (value === null || value === undefined || value === 0) return 'INR --';
        const num = typeof value === 'number' ? value : parseFloat(value);
        if (!Number.isFinite(num)) return 'INR --';
        return `INR ${num.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
    };

    // Group stocks by exchange and take only the first one for each exchange
    const groupedStocks = useMemo(() => {
        const groups = {
            'NSE': [],
            'BSE': [],
            'MCX': []
        };

        // Process gainers and losers from marketMovers
        const gainers = Array.isArray(marketMovers?.gainers) ? marketMovers.gainers : [];
        const losers = Array.isArray(marketMovers?.losers) ? marketMovers.losers : [];

        // Add gainers to their respective groups
        gainers.forEach(item => {
            const exchange = (item.exchange || 'NSE').toUpperCase();
            if (groups[exchange]) {
                groups[exchange].push(item);
            }
        });

        // Add losers to their respective groups if not already in gainers
        losers.forEach(item => {
            const exchange = (item.exchange || 'NSE').toUpperCase();
            if (groups[exchange] && !groups[exchange].find(g => g.symbol === item.symbol)) {
                groups[exchange].push(item);
            }
        });

        // Return the first stock from each exchange group, or fallback if none
        return [
            groups.NSE[0] || fallbackStocks.find(s => s.exchange === 'NSE') || { symbol: 'RELIANCE', exchange: 'NSE', price: 0, change: 0 },
            groups.BSE[0] || fallbackStocks.find(s => s.exchange === 'BSE') || { symbol: 'SENSEX', exchange: 'BSE', price: 0, change: 0 },
            groups.MCX[0] || fallbackStocks.find(s => s.exchange === 'MCX') || { symbol: 'CRUDEOIL', exchange: 'MCX', price: 0, change: 0 }
        ];
    }, [marketMovers]);

    // Don't render if loading or no data
    if (loading) return null;

    return (
        <div className="w-full bg-slate-900 border-b border-slate-800 py-2 overflow-hidden relative h-16 flex flex-col justify-center">
            {/* NSE Line */}
            <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12 mb-1">
                <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                    <div className="flex flex-col">
                        <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(groupedStocks[0]?.exchange)}`}>
                            {groupedStocks[0]?.exchange || 'NSE'}
                        </span>
                        <span className="text-[11px] font-black text-white uppercase tracking-tight">{groupedStocks[0]?.symbol || 'RELIANCE'}</span>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[11px] font-black text-white">{formatPrice(groupedStocks[0]?.price)}</span>
                        <div className={`flex items-center gap-0.5 text-[9px] font-bold ${parseFloat(groupedStocks[0]?.change || 0) >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                            {parseFloat(groupedStocks[0]?.change || 0) >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                            {parseFloat(groupedStocks[0]?.change || 0) >= 0 ? '+' : ''}{typeof groupedStocks[0]?.change === 'number' ? groupedStocks[0].change.toFixed(2) : '0.00'}%
                        </div>
                    </div>
                </div>
            </div>

            {/* BSE Line */}
            <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12 mb-1">
                <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                    <div className="flex flex-col">
                        <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(groupedStocks[1]?.exchange)}`}>
                            {groupedStocks[1]?.exchange || 'BSE'}
                        </span>
                        <span className="text-[11px] font-black text-white uppercase tracking-tight">{groupedStocks[1]?.symbol || 'SENSEX'}</span>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[11px] font-black text-white">{formatPrice(groupedStocks[1]?.price)}</span>
                        <div className={`flex items-center gap-0.5 text-[9px] font-bold ${parseFloat(groupedStocks[1]?.change || 0) >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                            {parseFloat(groupedStocks[1]?.change || 0) >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                            {parseFloat(groupedStocks[1]?.change || 0) >= 0 ? '+' : ''}{typeof groupedStocks[1]?.change === 'number' ? groupedStocks[1].change.toFixed(2) : '0.00'}%
                        </div>
                    </div>
                </div>
            </div>

            {/* MCX Line */}
            <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12">
                <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                    <div className="flex flex-col">
                        <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(groupedStocks[2]?.exchange)}`}>
                            {groupedStocks[2]?.exchange || 'MCX'}
                        </span>
                        <span className="text-[11px] font-black text-white uppercase tracking-tight">{groupedStocks[2]?.symbol || 'CRUDEOIL'}</span>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[11px] font-black text-white">{formatPrice(groupedStocks[2]?.price)}</span>
                        <div className={`flex items-center gap-0.5 text-[9px] font-bold ${parseFloat(groupedStocks[2]?.change || 0) >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                            {parseFloat(groupedStocks[2]?.change || 0) >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                            {parseFloat(groupedStocks[2]?.change || 0) >= 0 ? '+' : ''}{typeof groupedStocks[2]?.change === 'number' ? groupedStocks[2].change.toFixed(2) : '0.00'}%
                        </div>
                    </div>
                </div>
            </div>

            {/* Live indicator overlay */}
            <div className="absolute left-0 top-0 h-full bg-slate-900 px-4 flex items-center border-r border-slate-800 z-10 shadow-2xl">
                <div className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse shadow-[0_0_8px_#2DBD42]" />
                    <span className="text-[8px] font-black text-white uppercase tracking-[0.2em]">Market Watch</span>
                </div>
            </div>
        </div>
    );
}