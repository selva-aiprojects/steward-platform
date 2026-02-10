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
        <div className="w-full bg-slate-900 overflow-hidden h-[15px] flex items-center text-[6px]">
            <div className="flex items-center gap-1 px-1.5 bg-slate-800 h-full min-w-[40px]">
                <div className="h-0.5 w-0.5 rounded-full bg-green-500 animate-pulse" />
                <span className="font-black text-white uppercase tracking-tighter">LIVE</span>
            </div>

            {/* Ticker Animation Container */}
            <div className="flex-1 overflow-hidden h-full">
                <div className="flex items-center h-full">
                    <div className="flex animate-ticker-marquee whitespace-nowrap h-full items-center">
                        {tickers.map((item, index) => (
                            <TickerItem key={`${item.symbol}-${index}`} item={item} />
                        ))}
                        {/* Duplicate items for seamless loop */}
                        {tickers.map((item, index) => (
                            <TickerItem key={`duplicate-${item.symbol}-${index}`} item={item} />
                        ))}
                    </div>
                </div>
            </div>

            <style jsx>{`
                @keyframes ticker-marquee {
                    0% { transform: translateX(100%); }
                    100% { transform: translateX(-100%); }
                }
                .animate-ticker-marquee {
                    animation: ticker-marquee 40s linear infinite;
                    display: inline-block;
                    height: 100%;
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
        <div className="h-full flex items-center mx-1.5 px-1 py-0.25 border border-slate-700/50 rounded-sm bg-slate-800/30">
            <div className="flex items-center gap-0.5 mr-1">
                <span className="font-bold text-slate-200">{item.symbol}</span>
                {item.exchange && (
                    <span className="text-[5px] text-slate-400 uppercase">{item.exchange}</span>
                )}
            </div>
            <div className="flex items-center gap-0.25">
                <span className="font-bold text-slate-300">₹{priceLabel || '--'}</span>
                <div className={`flex items-center gap-0.25 ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
                    {isUp ? <TrendingUp size={6} /> : <TrendingDown size={6} />}
                    <span className="font-black text-[5.5px]">{changeLabel}</span>
                </div>
            </div>
        </div>
    );
}
