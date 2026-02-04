import React, { useState, useEffect } from "react";
import { MoveUp, MoveDown, Loader2 } from "lucide-react";
import { socket, fetchMarketMovers } from "../services/api";

export function TopMovers() {
    const [movers, setMovers] = useState({ gainers: [], losers: [] });
    const [activeTab, setActiveTab] = useState("GAINERS");
    const [loading, setLoading] = useState(true);
    const fallbackMovers = {
        gainers: [
            { symbol: 'RELIANCE', exchange: 'NSE', price: 2987.5, change: 1.2 },
            { symbol: 'HDFCBANK', exchange: 'NSE', price: 1450, change: 0.8 },
            { symbol: 'SENSEX', exchange: 'BSE', price: 72150, change: 0.6 }
        ],
        losers: [
            { symbol: 'CRUDEOIL', exchange: 'MCX', price: 6985, change: -0.4 },
            { symbol: 'TCS', exchange: 'NSE', price: 3450, change: -0.5 },
            { symbol: 'BOM500002', exchange: 'BSE', price: 1790, change: -0.45 }
        ]
    };

    useEffect(() => {
        const loadInitial = async () => {
            const data = await fetchMarketMovers();
            if (data) {
                if (data.gainers) setMovers(data);
                else if (Array.isArray(data)) {
                    // Handle array format if returned
                    setMovers({ gainers: data.slice(0, 5), losers: [] });
                }
            }
            if ((!data || (!data.gainers && !data.length)) && movers.gainers.length === 0) {
                setMovers(fallbackMovers);
            }
            setLoading(false);
        };

        loadInitial();

        // Socket listener for real-time updates
        socket.on('market_movers', (data) => {
            setMovers(data);
        });

        const interval = setInterval(loadInitial, 15000);
        return () => {
            socket.off('market_movers');
            clearInterval(interval);
        };
    }, []);

    const List = ({ items, type }) => (
        <div className="space-y-3">
            {items.length === 0 ? (
                <div className="text-center py-6 text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                    Waiting for Market Data...
                </div>
            ) : items.map((item, i) => (
                (() => {
                    const changeValue = typeof item.change === 'string' ? parseFloat(item.change) : (item.change ?? 0);
                    const changeLabel = typeof item.change === 'string' && item.change.includes('%')
                        ? item.change
                        : `${changeValue >= 0 ? '+' : ''}${changeValue}%`;
                    return (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl hover:bg-white hover:shadow-sm transition-all border border-slate-100">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${type === 'UP' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                            {type === 'UP' ? <MoveUp size={14} /> : <MoveDown size={14} />}
                        </div>
                        <div>
                            <p className="font-black text-slate-900 text-xs">{item.symbol}</p>
                            <p className="text-[10px] text-slate-400 font-bold">{"\u20B9"} {item.price}</p>
                            <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">{item.exchange || 'NSE'}</p>
                        </div>
                    </div>
                    <div className={`text-xs font-black ${type === 'UP' ? 'text-green-600' : 'text-red-500'}`}>
                        {changeLabel}
                    </div>
                </div>
                    );
                })()
            ))}
        </div>
    );

    return (
        <div data-testid="top-movers-container" className="p-6 bg-white rounded-2xl border border-slate-100 shadow-sm h-full">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="font-heading font-black text-slate-900 text-base">Market Movers</h3>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="h-1.5 w-1.5 bg-green-500 rounded-full animate-ping" />
                        <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">Live Market Feed</span>
                    </div>
                </div>
                <div className="flex bg-slate-100 p-1 rounded-lg">
                    <button
                        data-testid="gainers-tab"
                        onClick={() => setActiveTab("GAINERS")}
                        className={`px-3 py-1.5 rounded-md text-[10px] font-black uppercase tracking-wider transition-all ${activeTab === 'GAINERS' ? 'bg-white text-green-600 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
                    >
                        Gainers
                    </button>
                    <button
                        data-testid="losers-tab"
                        onClick={() => setActiveTab("LOSERS")}
                        className={`px-3 py-1.5 rounded-md text-[10px] font-black uppercase tracking-wider transition-all ${activeTab === 'LOSERS' ? 'bg-white text-red-600 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
                    >
                        Losers
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="h-40 flex flex-col items-center justify-center text-slate-400">
                    <Loader2 className="animate-spin mb-2" size={20} />
                    <span className="text-[10px] font-bold uppercase tracking-widest">Scanning market...</span>
                </div>
            ) : (
                <div className="animate-in fade-in duration-500">
                    {activeTab === "GAINERS" ? <List items={movers.gainers} type="UP" /> : <List items={movers.losers} type="DOWN" />}
                </div>
            )}
        </div>
    );
}

