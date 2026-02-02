import React, { useState, useEffect } from 'react';
import { socket } from '../services/api';
import { ArrowUp, ArrowDown, Activity } from 'lucide-react';

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

    // Convert updates map to array for display
    useEffect(() => {
        const items = Object.values(updates);
        // Ensure we have enough items for a smooth loop by duplicating if needed
        if (items.length > 0) {
            setTickers(items);
        }
    }, [updates]);

    if (tickers.length === 0) return null;

    return (
        <div className="w-full bg-slate-900 border-b border-slate-800 overflow-hidden h-10 flex items-center relative z-20">
            <div className="flex items-center gap-2 px-4 bg-slate-900 z-10 h-full border-r border-slate-800 shadow-xl">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[10px] font-black text-white uppercase tracking-widest whitespace-nowrap">NSE Live</span>
            </div>

            {/* Ticker Animation Container */}
            <div className="flex animate-ticker hover:pause-animation">
                {/* First Set */}
                <div className="flex items-center gap-8 pr-8">
                    {tickers.map((item) => (
                        <TickerItem key={`${item.symbol}-1`} item={item} />
                    ))}
                </div>
                {/* Duplicate Set for Seamless Loop */}
                <div className="flex items-center gap-8 pr-8">
                    {tickers.map((item) => (
                        <TickerItem key={`${item.symbol}-2`} item={item} />
                    ))}
                </div>
            </div>

        </div>
    );
}

function TickerItem({ item }) {
    const isUp = item.type === 'up';
    return (
        <div className="flex items-center gap-2 opacity-80 hover:opacity-100 transition-opacity cursor-default">
            <span className="text-[11px] font-bold text-slate-300">{item.symbol}</span>
            <div className={`flex items-center gap-1 text-[11px] font-black ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                <span>{item.price}</span>
                {isUp ? <ArrowUp size={10} /> : <ArrowDown size={10} />}
                <span>{item.change}</span>
            </div>
        </div>
    );
}
