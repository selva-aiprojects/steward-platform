import React, { useState, useEffect } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";
import { useAppData } from "../context/AppDataContext";

export function MarketTicker() {
    const { marketMovers, loading } = useAppData() || {};
    const [nseItems, setNseItems] = useState([]);
    const [bseItems, setBseItems] = useState([]);

    useEffect(() => {
        if (!marketMovers) {
            setNseItems([]);
            setBseItems([]);
            return;
        }

        const gainers = Array.isArray(marketMovers.gainers) ? marketMovers.gainers : [];
        const losers = Array.isArray(marketMovers.losers) ? marketMovers.losers : [];

        const all = [...gainers, ...losers].filter(
            (s) => s && s.symbol && Number.isFinite(Number(s.price))
        );

        // Separate items by exchange with fallback logic
        const nseFiltered = [];
        const bseFiltered = [];
        const otherItems = []; // For items without clear exchange designation

        all.forEach(item => {
            const exchange = item.exchange ? item.exchange.toUpperCase() : '';
            if (exchange.includes('NSE') || exchange.includes('XNSE') || exchange === 'NATIONAL STOCK EXCHANGE OF INDIA') {
                nseFiltered.push(item);
            } else if (exchange.includes('BSE') || exchange.includes('XBOM') || exchange === 'BOMBAY STOCK EXCHANGE') {
                bseFiltered.push(item);
            } else {
                // If exchange is not clearly identified, distribute evenly or use as fallback
                otherItems.push(item);
            }
        });

        // If we don't have enough items for each exchange, use otherItems as fallback
        if (nseFiltered.length < 5 && otherItems.length > 0) {
            const needed = 5 - nseFiltered.length;
            const additionalNse = otherItems.splice(0, needed);
            nseFiltered.push(...additionalNse);
        }

        if (bseFiltered.length < 5 && otherItems.length > 0) {
            const needed = 5 - bseFiltered.length;
            const additionalBse = otherItems.splice(0, needed);
            bseFiltered.push(...additionalBse);
        }

        // If still not enough items, duplicate existing ones to ensure continuous scrolling
        if (nseFiltered.length > 0 && nseFiltered.length < 10) {
            const duplicatesNeeded = 10 - nseFiltered.length;
            const duplicates = [];
            for (let i = 0; i < duplicatesNeeded; i++) {
                duplicates.push({...nseFiltered[i % nseFiltered.length], id: `dup-nse-${i}`});
            }
            nseFiltered.push(...duplicates);
        }

        if (bseFiltered.length > 0 && bseFiltered.length < 10) {
            const duplicatesNeeded = 10 - bseFiltered.length;
            const duplicates = [];
            for (let i = 0; i < duplicatesNeeded; i++) {
                duplicates.push({...bseFiltered[i % bseFiltered.length], id: `dup-bse-${i}`});
            }
            bseFiltered.push(...duplicates);
        }

        setNseItems(nseFiltered);
        setBseItems(bseFiltered);
    }, [marketMovers]);

    const formatPrice = (price) => {
        const num = Number(price);
        if (!Number.isFinite(num)) return "--";
        return num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
    };

    if (loading) return null;

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

    // Function to render a ticker row
    const renderTickerRow = (items, exchangeLabel) => {
        if (items.length === 0) return null;

        // Calculate animation duration based on number of items for consistent speed
        const baseDuration = 15; // Base duration in seconds
        const itemsCount = items.length;
        // More items = longer duration to maintain consistent speed
        const calculatedDuration = Math.max(15, baseDuration + (itemsCount * 0.5));

        return (
            <div className="flex items-center h-[40px] text-[10px]">
                <div className="flex items-center gap-2 px-3 bg-slate-800 h-full min-w-[80px]">
                    <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                    <span className="font-black text-white uppercase tracking-tight text-[9px]">
                        {exchangeLabel}
                    </span>
                </div>

                <div className="flex-1 overflow-hidden h-full ticker-container">
                    <div className="flex items-center h-full">
                        <div
                            className="flex animate-ticker-marquee whitespace-nowrap h-full items-center justify-start"
                            style={{ animationDuration: `${calculatedDuration}s` }}
                        >
                            {/* First copy */}
                            {items.map((item, index) => (
                                <TickerItem key={`ticker-${exchangeLabel}-${item.symbol}-${index}`} item={item} />
                            ))}
                            {/* Second copy for seamless loop */}
                            {items.map((item, index) => (
                                <TickerItem
                                    key={`ticker-duplicate-${exchangeLabel}-${item.symbol}-${index}`}
                                    item={item}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <>
            <div className="w-full bg-slate-900 overflow-hidden flex flex-col shadow-lg">
                {/* NSE Row */}
                {renderTickerRow(nseItems, "NSE ")}

                {/* BSE Row */}
                {renderTickerRow(bseItems, "BSE ")}
            </div>
            <style>{`
                @keyframes ticker-marquee {
                    from { transform: translateX(100%); }
                    to { transform: translateX(-100%); }
                }
                .animate-ticker-marquee {
                    animation: ticker-marquee 30s linear infinite;
                    display: inline-flex;
                    height: 100%;
                    width: auto;
                }
            `}</style>
        </>
    );
}
