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

    // Sort items alphabetically by symbol
    const sortedItems = [...all].sort((a, b) => a.symbol.localeCompare(b.symbol));

    // For the header ticker, show only a few items to keep it compact
    return sortedItems.slice(0, 5); // Limit to 5 items for header
  }, [marketMovers]);

  const formatPrice = (price: any) => {
    const num = Number(price);
    if (!Number.isFinite(num)) return "--";
    return num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
  };

  if (loading || allItems.length === 0) return null;

  // Separate tickers by exchange
  const nseItems = allItems.filter(item => item.exchange === 'NSE');
  const bseItems = allItems.filter(item => item.exchange === 'BSE');

  const TickerItem = ({ item }: { item: any }) => {
    const change = Number(item.change_pct ?? item.change ?? 0);
    const isUp = change >= 0;

    return (
      <div className="h-full flex items-center mx-3 px-3 py-1.5 border border-slate-600/50 rounded-lg bg-slate-800/70 shadow-md">
        <div className="flex items-center gap-1.5 mr-2">
          <span className="font-black text-slate-100 text-[10px] tracking-tight">{item.symbol}</span>
          {item.exchange && (
            <span className="text-[8px] text-slate-300 uppercase font-bold">{item.exchange}</span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <span className="font-bold text-slate-200 text-[10px]">₹{formatPrice(item.price)}</span>
          <div className={`flex items-center gap-1 ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
            {isUp ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            <span className="font-black text-[8px]">{isUp ? '+' : ''}{change.toFixed(2)}%</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full bg-slate-900 overflow-hidden flex flex-col shadow-lg">
      {/* Single Row for Header Ticker */}
      <div className="flex items-center h-[35px] text-[10px]">
        <div className="flex items-center gap-2 px-3 bg-slate-800 h-full min-w-[80px]">
          <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
          <span className="font-black text-white uppercase tracking-tight text-[9px]">LIVE</span>
        </div>

        {/* Ticker Animation Container */}
        <div className="flex-1 overflow-hidden h-full">
          <div className="flex items-center h-full">
            <div className="flex animate-ticker-marquee whitespace-nowrap h-full items-center">
              {allItems.map((item, index) => (
                <TickerItem key={`header-${item.symbol}-${index}`} item={item} />
              ))}
              {/* Duplicate items for seamless loop */}
              {allItems.map((item, index) => (
                <TickerItem key={`header-duplicate-${item.symbol}-${index}`} item={item} />
              ))}
            </div>
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
