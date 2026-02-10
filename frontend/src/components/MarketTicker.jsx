import React, { useMemo } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";
import { useAppData } from "../context/AppDataContext";

export function MarketTicker() {
  const { marketMovers, loading } = useAppData() || {};

  const allItems = useMemo(() => {
    if (!marketMovers) return [];

    const gainers = Array.isArray(marketMovers.gainers) ? marketMovers.gainers : [];
    const losers = Array.isArray(marketMovers.losers) ? marketMovers.losers : [];

    // Combine gainers and losers and filter valid items
    const all = [...gainers, ...losers].filter(
      (s) => s && s.symbol && s.exchange && Number.isFinite(Number(s.price))
    );

    // Limit to top items to avoid clutter
    return all.slice(0, 20); // Limit to 20 items total
  }, [marketMovers]);

  const formatPrice = (price: any) => {
    const num = Number(price);
    if (!Number.isFinite(num)) return "--";
    return num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
  };

  if (loading || allItems.length === 0) return null;

  const TickerItem = ({ item }: { item: any }) => {
    const change = Number(item.change_pct ?? item.change ?? 0);
    const isUp = change >= 0;

    return (
      <div className="flex items-center gap-1.5 mx-3 px-2 py-0.5 border border-slate-700/50 rounded-sm bg-slate-800/30 min-w-[120px]">
        <div className="flex items-center gap-0.5 mr-1">
          <span className="text-[7px] font-bold text-slate-200">{item.symbol}</span>
          <span className="text-[6px] text-slate-400 uppercase">{item.exchange}</span>
        </div>
        <div className="flex items-center gap-0.5">
          <span className="text-[7px] font-bold text-slate-300">₹{formatPrice(item.price)}</span>
          <div className={`flex items-center gap-0.5 ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
            {isUp ? <TrendingUp size={6} /> : <TrendingDown size={6} />}
            <span className="text-[6px] font-black">{isUp ? '+' : ''}{change.toFixed(2)}%</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full bg-slate-900 overflow-hidden h-[15px] flex items-center text-[6px]">
      <div className="flex items-center gap-1 px-2 bg-slate-800 h-full min-w-[50px]">
        <div className="h-0.5 w-0.5 rounded-full bg-green-500 animate-pulse" />
        <span className="font-black text-white uppercase tracking-tighter">LIVE</span>
      </div>

      {/* Ticker Animation Container */}
      <div className="flex-1 overflow-hidden h-full">
        <div className="flex items-center h-full">
          <div className="flex animate-ticker-marquee whitespace-nowrap h-full items-center">
            {allItems.map((item, index) => (
              <TickerItem key={`market-${item.symbol}-${index}`} item={item} />
            ))}
            {/* Duplicate items for seamless loop */}
            {allItems.map((item, index) => (
              <TickerItem key={`market-duplicate-${item.symbol}-${index}`} item={item} />
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
          animation: ticker-marquee 45s linear infinite;
          display: inline-block;
          height: 100%;
        }
      `}</style>
    </div>
  );
}
