import React, { useMemo } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";
import { useAppData } from "../context/AppDataContext";

export function MarketTicker() {
    const { marketMovers, loading } = useAppData() || {};

    // ✅ Normalize Live Data Only (NO FALLBACKS)
    const liveStocks = useMemo(() => {
        if (!marketMovers) return [];

        const gainers = Array.isArray(marketMovers.gainers)
            ? marketMovers.gainers
            : [];

        const losers = Array.isArray(marketMovers.losers)
            ? marketMovers.losers
            : [];

        // Merge and keep only valid live items
        return [...gainers, ...losers]
            .filter(
                (s) =>
                    s &&
                    s.symbol &&
                    s.exchange &&
                    Number.isFinite(Number(s.price))
            )
            .slice(0, 12); // Professional ticker usually limits count
    }, [marketMovers]);

    // ✅ Exchange Styling
    const exchangeClass = (exchange = "") => {
        switch (exchange.toUpperCase()) {
            case "NSE":
                return "text-emerald-400 border-emerald-500/40";
            case "BSE":
                return "text-sky-400 border-sky-500/40";
            case "MCX":
                return "text-amber-400 border-amber-500/40";
            default:
                return "text-slate-400 border-slate-500/40";
        }
    };

    // ✅ Format Price
    const formatPrice = (price) => {
        const num = Number(price);
        if (!Number.isFinite(num)) return "--";
        return num.toLocaleString("en-IN", {
            maximumFractionDigits: 2,
        });
    };

    // ❌ Do NOT Render If No Live Data
    if (loading || liveStocks.length === 0) return null;

    // ✅ Professional Card
    const TickerItem = ({ item }) => {
        const change = Number(item.change || 0);
        const isUp = change >= 0;

        return (
            <div className="flex items-center gap-4 bg-slate-800/60 backdrop-blur px-4 py-2 rounded-xl border border-slate-700/60 min-w-[200px] shadow-lg">
                {/* Exchange + Symbol */}
                <div className="flex flex-col">
          <span
              className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border ${exchangeClass(
                  item.exchange
              )}`}
          >
            {item.exchange}
          </span>

                    <span className="text-sm font-bold text-white">
            {item.symbol}
          </span>
                </div>

                {/* Price + Change */}
                <div className="flex flex-col items-end ml-auto">
          <span className="text-sm font-bold text-white">
            ₹ {formatPrice(item.price)}
          </span>

                    <div
                        className={`flex items-center gap-1 text-xs font-semibold ${
                            isUp ? "text-emerald-400" : "text-red-400"
                        }`}
                    >
                        {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                        {isUp ? "+" : ""}
                        {change.toFixed(2)}%
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="w-full bg-slate-950 border-b border-slate-800 relative overflow-hidden">
            {/* Live Label */}
            <div className="absolute left-0 top-0 h-full px-5 flex items-center bg-slate-950 border-r border-slate-800 z-20">
                <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-[10px] font-bold text-white tracking-widest">
            LIVE MARKET
          </span>
                </div>
            </div>

            {/* Professional Smooth Scroll */}
            <div className="flex gap-6 pl-36 pr-6 py-3 animate-[ticker_40s_linear_infinite] whitespace-nowrap">
                {liveStocks.map((stock, i) => (
                    <TickerItem key={stock.symbol + i} item={stock} />
                ))}
            </div>
        </div>
    );
}
