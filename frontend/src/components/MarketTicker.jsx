import React, { useState, useEffect } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";
import { useAppData } from "../context/AppDataContext";

export function MarketTicker() {
    const { marketMovers, loading } = useAppData() || {};
    const [allItems, setAllItems] = useState([]);

    useEffect(() => {
        if (!marketMovers) {
            setAllItems([]);
            return;
        }

        const gainers = Array.isArray(marketMovers.gainers) ? marketMovers.gainers : [];
        const losers = Array.isArray(marketMovers.losers) ? marketMovers.losers : [];

        const all = [...gainers, ...losers].filter(
            (s) => s && s.symbol && s.exchange && Number.isFinite(Number(s.price))
        );

        const sortedItems = [...all].sort((a, b) =>
            String(a.symbol).localeCompare(String(b.symbol))
        );

        setAllItems(sortedItems);
    }, [marketMovers]);

    const formatPrice = (price) => {
        const num = Number(price);
        if (!Number.isFinite(num)) return "--";
        return num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
    };

    if (loading || allItems.length === 0) return null;

    const TickerItem = ({ item }) => {
        const change = Number(
            item.change_pct !== undefined ? item.change_pct : item.change ?? 0
        );
        const isUp = change >= 0;

        return (
            <div className="h-full flex items-center mx-1.5 px-2 py-1 border border-slate-600/50 rounded-md bg-slate-800/70 shadow-sm min-w-fit">
                <div className="flex items-center gap-1 mr-1">
          <span className="font-black text-slate-100 text-[9px] tracking-tight">
            {item.symbol}
          </span>
                    {item.exchange && (
                        <span className="text-[7px] text-slate-300 uppercase font-bold">
              {item.exchange}
            </span>
                    )}
                </div>
                <div className="flex items-center gap-0.5">
          <span className="font-bold text-slate-200 text-[9px]">
            ₹{formatPrice(item.price)}
          </span>
                    <div
                        className={`flex items-center gap-0.5 ${
                            isUp ? "text-emerald-400" : "text-red-400"
                        }`}
                    >
                        {isUp ? <TrendingUp size={8} /> : <TrendingDown size={8} />}
                        <span className="font-black text-[7px]">
              {isUp ? "+" : ""}
                            {change.toFixed(2)}%
            </span>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="w-full bg-slate-900 overflow-hidden flex flex-col shadow-lg">
            <div className="flex items-center h-[40px] text-[10px]">
                <div className="flex items-center gap-2 px-3 bg-slate-800 h-full min-w-[80px]">
                    <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                    <span className="font-black text-white uppercase tracking-tight text-[9px]">
            LIVE
          </span>
                </div>

                <div className="flex-1 overflow-hidden h-full ticker-container">
                    <div className="flex items-center h-full">
                        <div className="flex animate-ticker-marquee whitespace-nowrap h-full items-center justify-start">
                            {/* First copy */}
                            {allItems.map((item, index) => (
                                <TickerItem key={`header-${item.symbol}-${index}`} item={item} />
                            ))}
                            {/* Second copy for seamless loop */}
                            {allItems.map((item, index) => (
                                <TickerItem
                                    key={`header-duplicate-${item.symbol}-${index}`}
                                    item={item}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
