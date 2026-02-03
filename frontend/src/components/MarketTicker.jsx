import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Zap } from 'lucide-react';
import { socket } from '../services/api';

export function MarketTicker() {
    const [stocks, setStocks] = useState([]);

    useEffect(() => {
        const handleUpdate = (data) => {
            setStocks(prev => {
                const exists = prev.find(s => s.symbol === data.symbol);
                if (exists) {
                    return prev.map(s => s.symbol === data.symbol ? { ...s, ...data } : s);
                }
                return [data, ...prev].slice(0, 15);
            });
        };

        socket.on('market_update', handleUpdate);
        return () => socket.off('market_update', handleUpdate);
    }, []);

    if (stocks.length === 0) return null;

    return (
        <div className="w-full bg-slate-900 border-b border-slate-800 py-2 overflow-hidden relative h-12 flex items-center">
            <div className="flex animate-marquee whitespace-nowrap gap-8 pr-12">
                {[...stocks, ...stocks].map((stock, i) => (
                    <div key={i} className="flex items-center gap-4 bg-slate-800/50 px-4 py-1.5 rounded-lg border border-slate-700/50">
                        <div className="flex flex-col">
                            <span className="text-[7px] font-black text-primary uppercase tracking-[0.2em] leading-none mb-0.5">{stock.exchange || 'NSE'}</span>
                            <span className="text-[10px] font-black text-white uppercase tracking-tight">{stock.symbol}</span>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] font-black text-white">₹{stock.price?.toLocaleString()}</span>
                            <div className={`flex items-center gap-0.5 text-[8px] font-bold ${parseFloat(stock.change) >= 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                {parseFloat(stock.change) >= 0 ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                                {parseFloat(stock.change) >= 0 ? '+' : ''}{stock.change}%
                            </div>
                        </div>
                    </div>
                ))}
            </div>

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
