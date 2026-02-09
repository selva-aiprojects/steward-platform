import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { useAppData } from '../context/AppDataContext';

export function MarketTicker() {
    const { marketMovers, loading } = useAppData();
    
    // Define fallback stocks for each exchange
    const fallbackStocks = {
        NSE: { symbol: 'RELIANCE', exchange: 'NSE', price: 2987.5, change: 1.2 },
        BSE: { symbol: 'SENSEX', exchange: 'BSE', price: 72150, change: 0.6 },
        MCX: { symbol: 'CRUDEOIL', exchange: 'MCX', price: 6985, change: -0.4 }
    };

    // Extract gainers and losers from marketMovers
    let gainers = [];
    let losers = [];
    
    if (Array.isArray(marketMovers)) {
        // If marketMovers is an array, treat it as the main list
        gainers = marketMovers;
    } else if (marketMovers && typeof marketMovers === 'object') {
        // If marketMovers is an object with gainers/losers properties
        gainers = Array.isArray(marketMovers.gainers) ? marketMovers.gainers : [];
        losers = Array.isArray(marketMovers.losers) ? marketMovers.losers : [];
    }
    
    // Get stock for each exchange (first from gainers, then from losers, then fallback)
    const getStockForExchange = (exchange) => {
        // Find in gainers first
        const fromGainers = gainers.find(item => 
            (item.exchange || 'NSE').toUpperCase() === exchange.toUpperCase()
        );
        
        if (fromGainers) {
            return {
                symbol: fromGainers.symbol || fallbackStocks[exchange]?.symbol,
                exchange: fromGainers.exchange || exchange,
                price: fromGainers.price || fromGainers.last_price || fallbackStocks[exchange]?.price,
                change: fromGainers.change || fromGainers.percent_change || fallbackStocks[exchange]?.change
            };
        }
        
        // Find in losers if not in gainers
        const fromLosers = losers.find(item => 
            (item.exchange || 'NSE').toUpperCase() === exchange.toUpperCase()
        );
        
        if (fromLosers) {
            return {
                symbol: fromLosers.symbol || fallbackStocks[exchange]?.symbol,
                exchange: fromLosers.exchange || exchange,
                price: fromLosers.price || fromLosers.last_price || fallbackStocks[exchange]?.price,
                change: fromLosers.change || fromLosers.percent_change || fallbackStocks[exchange]?.change
            };
        }
        
        // Return fallback if nothing found
        return fallbackStocks[exchange] || { symbol: 'N/A', exchange: exchange, price: 0, change: 0 };
    };

    // Get stocks for each exchange
    const nseStock = getStockForExchange('NSE');
    const bseStock = getStockForExchange('BSE');
    const mcxStock = getStockForExchange('MCX');

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

    // Don't render if loading or no data
    if (loading) return null;

    return (
        <div className="w-full bg-slate-900 border-b border-slate-800 py-2 overflow-hidden relative h-16 flex flex-col justify-center">
            {/* NSE Line */}
            <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12 mb-1">
                <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                    <div className="flex flex-col">
                        <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(nseStock?.exchange)}`}>
                            {nseStock?.exchange || 'NSE'}
                        </span>
                        <span className="text-[11px] font-black text-white uppercase tracking-tight">{nseStock?.symbol || 'RELIANCE'}</span>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[11px] font-black text-white">{formatPrice(nseStock?.price)}</span>
                        <div className={`flex items-center gap-0.5 text-[9px] font-bold ${nseStock?.change >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                            {nseStock?.change >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                            {nseStock?.change >= 0 ? '+' : ''}{typeof nseStock?.change === 'number' ? nseStock.change.toFixed(2) : '0.00'}%
                        </div>
                    </div>
                </div>
            </div>

            {/* BSE Line */}
            <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12 mb-1">
                <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                    <div className="flex flex-col">
                        <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(bseStock?.exchange)}`}>
                            {bseStock?.exchange || 'BSE'}
                        </span>
                        <span className="text-[11px] font-black text-white uppercase tracking-tight">{bseStock?.symbol || 'SENSEX'}</span>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[11px] font-black text-white">{formatPrice(bseStock?.price)}</span>
                        <div className={`flex items-center gap-0.5 text-[9px] font-bold ${bseStock?.change >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                            {bseStock?.change >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                            {bseStock?.change >= 0 ? '+' : ''}{typeof bseStock?.change === 'number' ? bseStock.change.toFixed(2) : '0.00'}%
                        </div>
                    </div>
                </div>
            </div>

            {/* MCX Line */}
            <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12">
                <div className="flex items-center gap-4 bg-slate-800/70 px-4 py-1.5 rounded-lg border border-slate-600/60 shadow-sm">
                    <div className="flex flex-col">
                        <span className={`text-[8px] font-black uppercase tracking-[0.18em] leading-none mb-0.5 px-1.5 py-0.5 rounded border ${exchangeClass(mcxStock?.exchange)}`}>
                            {mcxStock?.exchange || 'MCX'}
                        </span>
                        <span className="text-[11px] font-black text-white uppercase tracking-tight">{mcxStock?.symbol || 'CRUDEOIL'}</span>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[11px] font-black text-white">{formatPrice(mcxStock?.price)}</span>
                        <div className={`flex items-center gap-0.5 text-[9px] font-bold ${mcxStock?.change >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                            {mcxStock?.change >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                            {mcxStock?.change >= 0 ? '+' : ''}{typeof mcxStock?.change === 'number' ? mcxStock.change.toFixed(2) : '0.00'}%
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