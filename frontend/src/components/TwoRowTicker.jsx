import React, { useState, useEffect } from 'react';
import { socket } from '../services/api';
import { TrendingUp, TrendingDown } from 'lucide-react';

export function TwoRowTicker() {
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
                { symbol: 'ADANIPORTS', exchange: 'NSE', price: 1500.00, change: 0.5, type: 'up' },
                { symbol: 'ASIANPAINT', exchange: 'NSE', price: 3200.00, change: -0.3, type: 'down' },
                { symbol: 'AXISBANK', exchange: 'NSE', price: 1125.00, change: 0.9, type: 'up' },
                { symbol: 'BAJAJ-AUTO', exchange: 'NSE', price: 5800.00, change: 1.2, type: 'up' },
                { symbol: 'BAJFINANCE', exchange: 'NSE', price: 7200.00, change: 1.5, type: 'up' },
                { symbol: 'BHARTIARTL', exchange: 'NSE', price: 980.00, change: 0.8, type: 'up' },
                { symbol: 'BPCL', exchange: 'NSE', price: 450.00, change: -0.4, type: 'down' },
                { symbol: 'BRITANNIA', exchange: 'NSE', price: 4200.00, change: 0.6, type: 'up' },
                { symbol: 'CIPLA', exchange: 'NSE', price: 1200.00, change: 0.3, type: 'up' },
                { symbol: 'COALINDIA', exchange: 'NSE', price: 280.00, change: 0.7, type: 'up' },
                { symbol: 'DIVISLAB', exchange: 'NSE', price: 3800.00, change: 1.1, type: 'up' },
                { symbol: 'DRREDDY', exchange: 'NSE', price: 5200.00, change: -0.2, type: 'down' },
                { symbol: 'EICHERMOT', exchange: 'NSE', price: 3200.00, change: 0.9, type: 'up' },
                { symbol: 'GRASIM', exchange: 'NSE', price: 1800.00, change: -0.5, type: 'down' },
                { symbol: 'HCLTECH', exchange: 'NSE', price: 1300.00, change: 0.4, type: 'up' },
                { symbol: 'HDFC', exchange: 'NSE', price: 2800.00, change: 0.6, type: 'up' },
                { symbol: 'HDFCBANK', exchange: 'NSE', price: 1450.00, change: 0.8, type: 'up' },
                { symbol: 'HEROMOTOCO', exchange: 'NSE', price: 1400.00, change: 0.7, type: 'up' },
                { symbol: 'HINDALCO', exchange: 'NSE', price: 550.00, change: -0.3, type: 'down' },
                { symbol: 'HINDUNILVR', exchange: 'NSE', price: 2700.00, change: 0.5, type: 'up' },
                { symbol: 'ICICIBANK', exchange: 'NSE', price: 1042.00, change: -0.3, type: 'down' },
                { symbol: 'INDUSINDBK', exchange: 'NSE', price: 1200.00, change: 0.2, type: 'up' },
                { symbol: 'INFY', exchange: 'NSE', price: 1540.00, change: 0.6, type: 'up' },
                { symbol: 'IOC', exchange: 'NSE', price: 140.00, change: 0.4, type: 'up' },
                { symbol: 'ITC', exchange: 'NSE', price: 438.00, change: 0.4, type: 'up' },
                { symbol: 'JSWSTEEL', exchange: 'NSE', price: 750.00, change: 0.8, type: 'up' },
                { symbol: 'KOTAKBANK', exchange: 'NSE', price: 1800.00, change: -0.2, type: 'down' },
                { symbol: 'LT', exchange: 'NSE', price: 2200.00, change: -0.7, type: 'down' },
                { symbol: 'M&M', exchange: 'NSE', price: 1100.00, change: 0.5, type: 'up' },
                { symbol: 'MARUTI', exchange: 'NSE', price: 8500.00, change: 0.8, type: 'up' },
                { symbol: 'NESTLEIND', exchange: 'NSE', price: 22000.00, change: 0.9, type: 'up' },
                { symbol: 'NIFTY', exchange: 'NSE', price: 22340.00, change: 0.7, type: 'up' },
                { symbol: 'NTPC', exchange: 'NSE', price: 240.00, change: 0.3, type: 'up' },
                { symbol: 'ONGC', exchange: 'NSE', price: 180.00, change: -0.2, type: 'down' },
                { symbol: 'POWERGRID', exchange: 'NSE', price: 250.00, change: 0.4, type: 'up' },
                { symbol: 'RELIANCE', exchange: 'NSE', price: 2987.50, change: 1.2, type: 'up' },
                { symbol: 'SBIN', exchange: 'NSE', price: 580.00, change: 1.1, type: 'up' },
                { symbol: 'SUNPHARMA', exchange: 'NSE', price: 950.00, change: 0.6, type: 'up' },
                { symbol: 'TATAMOTORS', exchange: 'NSE', price: 750.00, change: 1.0, type: 'up' },
                { symbol: 'TATASTEEL', exchange: 'NSE', price: 1400.00, change: 0.7, type: 'up' },
                { symbol: 'TCS', exchange: 'NSE', price: 3450.00, change: -0.5, type: 'down' },
                { symbol: 'ULTRACEMCO', exchange: 'NSE', price: 9800.00, change: 0.8, type: 'up' },
                { symbol: 'UPL', exchange: 'NSE', price: 850.00, change: -0.4, type: 'down' },
                { symbol: 'WIPRO', exchange: 'NSE', price: 750.00, change: 0.5, type: 'up' },
                { symbol: 'YESBANK', exchange: 'NSE', price: 22.00, change: 1.3, type: 'up' },
                { symbol: 'ASHOKLEY', exchange: 'BSE', price: 180.00, change: 0.5, type: 'up' },
                { symbol: 'BAJAJFINSV', exchange: 'BSE', price: 16000.00, change: 0.8, type: 'up' },
                { symbol: 'BAJAJHLDNG', exchange: 'BSE', price: 3800.00, change: 0.6, type: 'up' },
                { symbol: 'BHEL', exchange: 'BSE', price: 45.00, change: 0.3, type: 'up' },
                { symbol: 'BPCL', exchange: 'BSE', price: 448.00, change: -0.2, type: 'down' },
                { symbol: 'CIPLA', exchange: 'BSE', price: 1195.00, change: 0.2, type: 'up' },
                { symbol: 'EICHERMOT', exchange: 'BSE', price: 3195.00, change: 0.8, type: 'up' },
                { symbol: 'GAIL', exchange: 'BSE', price: 200.00, change: 0.4, type: 'up' },
                { symbol: 'GRASIM', exchange: 'BSE', price: 1795.00, change: -0.4, type: 'down' },
                { symbol: 'HINDALCO', exchange: 'BSE', price: 548.00, change: -0.5, type: 'down' },
                { symbol: 'HINDMOTORS', exchange: 'BSE', price: 150.00, change: 0.7, type: 'up' },
                { symbol: 'IDEA', exchange: 'BSE', price: 12.00, change: 1.0, type: 'up' },
                { symbol: 'IOC', exchange: 'BSE', price: 138.00, change: 0.2, type: 'up' },
                { symbol: 'JINDALSTEL', exchange: 'BSE', price: 450.00, change: 0.6, type: 'up' },
                { symbol: 'JSWSTEEL', exchange: 'BSE', price: 745.00, change: 0.7, type: 'up' },
                { symbol: 'LT', exchange: 'BSE', price: 2195.00, change: -0.6, type: 'down' },
                { symbol: 'M&M', exchange: 'BSE', price: 1095.00, change: 0.4, type: 'up' },
                { symbol: 'MARUTI', exchange: 'BSE', price: 8490.00, change: 0.7, type: 'up' },
                { symbol: 'NATIONALUM', exchange: 'BSE', price: 180.00, change: 0.5, type: 'up' },
                { symbol: 'NMDC', exchange: 'BSE', price: 250.00, change: 0.8, type: 'up' },
                { symbol: 'ONGC', exchange: 'BSE', price: 178.00, change: -0.3, type: 'down' },
                { symbol: 'POWERGRID', exchange: 'BSE', price: 248.00, change: 0.3, type: 'up' },
                { symbol: 'RELIANCE', exchange: 'BSE', price: 2985.00, change: 1.1, type: 'up' },
                { symbol: 'SBIN', exchange: 'BSE', price: 578.00, change: 1.0, type: 'up' },
                { symbol: 'SUNPHARMA', exchange: 'BSE', price: 945.00, change: 0.5, type: 'up' },
                { symbol: 'TATAMOTORS', exchange: 'BSE', price: 745.00, change: 0.9, type: 'up' },
                { symbol: 'TATASTEEL', exchange: 'BSE', price: 1395.00, change: 0.6, type: 'up' },
                { symbol: 'WIPRO', exchange: 'BSE', price: 745.00, change: 0.4, type: 'up' }
            ]);
        }
    }, []);

    // Convert updates map to array for display and sort alphabetically
    useEffect(() => {
        const items = Object.values(updates);
        if (items.length > 0) {
            // Sort items alphabetically by symbol
            const sortedItems = [...items].sort((a, b) => a.symbol.localeCompare(b.symbol));
            setTickers(sortedItems);
        }
    }, [updates]);

    if (tickers.length === 0) return null;

    // Separate tickers by exchange
    const nseTickers = tickers.filter(item => item.exchange === 'NSE').sort((a, b) => a.symbol.localeCompare(b.symbol));
    const bseTickers = tickers.filter(item => item.exchange === 'BSE').sort((a, b) => a.symbol.localeCompare(b.symbol));

    return (
        <div className="w-full bg-slate-900 overflow-hidden flex flex-col shadow-lg">
            {/* NSE Row */}
            <div className="flex items-center h-[30px] text-[9px]">
                <div className="flex items-center gap-1.5 px-2 bg-emerald-700 h-full min-w-[70px]">
                    <div className="h-1 w-1 rounded-full bg-emerald-300 animate-pulse" />
                    <span className="font-black text-white uppercase tracking-tight text-[8px]">NSE</span>
                </div>

                {/* NSE Ticker Animation Container */}
                <div className="flex-1 overflow-hidden h-full">
                    <div className="flex items-center h-full">
                        <div className="flex animate-ticker-marquee-nse whitespace-nowrap h-full items-center">
                            {nseTickers.map((item, index) => (
                                <TickerItem key={`nse-${item.symbol}-${index}`} item={item} />
                            ))}
                            {/* Duplicate items for seamless loop */}
                            {nseTickers.map((item, index) => (
                                <TickerItem key={`nse-duplicate-${item.symbol}-${index}`} item={item} />
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* BSE Row */}
            <div className="flex items-center h-[30px] text-[9px] border-t border-slate-700">
                <div className="flex items-center gap-1.5 px-2 bg-sky-700 h-full min-w-[70px]">
                    <div className="h-1 w-1 rounded-full bg-sky-300 animate-pulse" />
                    <span className="font-black text-white uppercase tracking-tight text-[8px]">BSE</span>
                </div>

                {/* BSE Ticker Animation Container */}
                <div className="flex-1 overflow-hidden h-full">
                    <div className="flex items-center h-full">
                        <div className="flex animate-ticker-marquee-bse whitespace-nowrap h-full items-center">
                            {bseTickers.map((item, index) => (
                                <TickerItem key={`bse-${item.symbol}-${index}`} item={item} />
                            ))}
                            {/* Duplicate items for seamless loop */}
                            {bseTickers.map((item, index) => (
                                <TickerItem key={`bse-duplicate-${item.symbol}-${index}`} item={item} />
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <style jsx>{`
                @keyframes ticker-marquee-nse {
                    0% { transform: translateX(100%); }
                    100% { transform: translateX(-100%); }
                }
                @keyframes ticker-marquee-bse {
                    0% { transform: translateX(100%); }
                    100% { transform: translateX(-100%); }
                }
                .animate-ticker-marquee-nse {
                    animation: ticker-marquee-nse 40s linear infinite;
                    display: inline-block;
                    height: 100%;
                }
                .animate-ticker-marquee-bse {
                    animation: ticker-marquee-bse 45s linear infinite;
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
        <div className="h-full flex items-center mx-2 px-2.5 py-1 border border-slate-600/50 rounded-md bg-slate-800/50 shadow-sm">
            <div className="flex items-center gap-1 mr-2">
                <span className="font-black text-slate-100 text-[9px] tracking-tight">{item.symbol}</span>
                {item.exchange && (
                    <span className="text-[7px] text-slate-300 uppercase font-bold">{item.exchange}</span>
                )}
            </div>
            <div className="flex items-center gap-0.5">
                <span className="font-bold text-slate-200 text-[9px]">₹{priceLabel || '--'}</span>
                <div className={`flex items-center gap-0.5 ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
                    {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                    <span className="font-black text-[7px]">{changeLabel}</span>
                </div>
            </div>
        </div>
    );
}