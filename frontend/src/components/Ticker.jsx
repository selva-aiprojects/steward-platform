import React, { useState, useEffect } from 'react';
import { socket } from '../services/api';
import { TrendingUp, TrendingDown } from 'lucide-react';

export function Ticker() {
    const [updates, setUpdates] = useState({});
    const [tickers, setTickers] = useState([]);

    useEffect(() => {
        // Listen for individual stock updates
        socket.on('market_update', (data) => {
            setUpdates(prev => {
                const newUpdates = { ...prev, [data.symbol]: data };
                return newUpdates;
            });
        });

        return () => {
            socket.off('market_update');
        };
    }, []);

    // Initial Mock Data to ensure immediate visibility
    useEffect(() => {
        if (tickers.length === 0) {
            setTickers([
                { symbol: 'RELIANCE', exchange: 'NSE', price: 2987.50, change: 1.2, type: 'up' },
                { symbol: 'TCS', exchange: 'NSE', price: 3450.00, change: -0.5, type: 'down' },
                { symbol: 'HDFCBANK', exchange: 'NSE', price: 1450.00, change: 0.8, type: 'up' },
                { symbol: 'INFY', exchange: 'NSE', price: 1540.00, change: 0.6, type: 'up' },
                { symbol: 'ICICIBANK', exchange: 'NSE', price: 1042.00, change: -0.3, type: 'down' },
                { symbol: 'SBIN', exchange: 'NSE', price: 580.00, change: 1.1, type: 'up' },
                { symbol: 'ITC', exchange: 'NSE', price: 438.00, change: 0.4, type: 'up' },
                { symbol: 'LT', exchange: 'NSE', price: 2200.00, change: -0.7, type: 'down' },
                { symbol: 'AXISBANK', exchange: 'NSE', price: 1125.00, change: 0.9, type: 'up' },
                { symbol: 'KOTAKBANK', exchange: 'NSE', price: 1800.00, change: -0.2, type: 'down' },
                { symbol: 'BAJFINANCE', exchange: 'NSE', price: 7200.00, change: 1.5, type: 'up' },
                { symbol: 'MARUTI', exchange: 'NSE', price: 8500.00, change: 0.8, type: 'up' },
                { symbol: 'SENSEX', exchange: 'BSE', price: 72150.00, change: 0.6, type: 'up' },
                { symbol: 'NIFTY', exchange: 'NSE', price: 22340.00, change: 0.7, type: 'up' },
                { symbol: 'GOLD', exchange: 'MCX', price: 62450.00, change: 0.3, type: 'up' },
                { symbol: 'SILVER', exchange: 'MCX', price: 74200.00, change: -0.1, type: 'down' },
                { symbol: 'CRUDEOIL', exchange: 'MCX', price: 6985.00, change: -0.4, type: 'down' },
                { symbol: 'NATURALGAS', exchange: 'MCX', price: 280.00, change: 1.2, type: 'up' }
            ]);
        }
    }, []);

    // Convert updates map to array for display
    useEffect(() => {
        const items = Object.values(updates);
        if (items.length > 0) {
            setTickers(items);
        }
    }, [updates]);

    if (tickers.length === 0) return null;

    return (
        <div className="w-full bg-slate-900 border-b border-slate-800 overflow-hidden h-8 flex items-center relative z-20">
            <div className="flex items-center gap-2 px-3 bg-slate-900 z-10 h-full border-r border-slate-800">
                <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[9px] font-black text-white uppercase tracking-wider whitespace-nowrap">LIVE</span>
            </div>

            {/* Ticker Animation Container */}
            <div className="flex flex-1 overflow-hidden">
                <div className="flex animate-ticker-marquee whitespace-nowrap flex-1">
                    {tickers.map((item, index) => (
                        <TickerItem key={`${item.symbol}-${index}`} item={item} />
                    ))}
                    {/* Duplicate items for seamless loop */}
                    {tickers.map((item, index) => (
                        <TickerItem key={`duplicate-${item.symbol}-${index}`} item={item} />
                    ))}
                </div>
            </div>

            <style jsx>{`
                @keyframes ticker-marquee {
                    0% { transform: translateX(0); }
                    100% { transform: translateX(-50%); }
                }
                .animate-ticker-marquee {
                    animation: ticker-marquee 60s linear infinite;
                    display: inline-block;
                }
            `}</style>
        </div>
    );
}

function TickerItem({ item }) {
    const changeValue = typeof item.change === 'string' ? parseFloat(item.change) : (item.change ?? 0);
    const isUp = item.type ? item.type === 'up' : changeValue >= 0;
    const changeLabel = typeof item.change === 'string' && item.change.includes('%')
        ? item.change
        : `${changeValue >= 0 ? '+' : ''}${changeValue}%`;
    const priceLabel = typeof item.price === 'number'
        ? item.price.toLocaleString()
        : item.price;
    return (
        <div className="flex items-center gap-1.5 mx-4 px-2 py-1 border border-slate-700 rounded-md bg-slate-800/50">
            <div className="flex flex-col">
                <div className="flex items-center gap-1">
                    <span className="text-[9px] font-bold text-slate-200">{item.symbol}</span>
                    {item.exchange && (
                        <span className="text-[7px] font-black text-slate-400 uppercase">{item.exchange}</span>
                    )}
                </div>
                <div className="flex items-center gap-1">
                    <span className="text-[8px] font-bold text-slate-300">₹{priceLabel || '--'}</span>
                </div>
            </div>
            <div className={`flex items-center gap-0.5 min-w-[40px] justify-center px-1 rounded ${isUp ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                <span className="text-[8px] font-black">{changeLabel}</span>
            </div>
        </div>
    );
}
