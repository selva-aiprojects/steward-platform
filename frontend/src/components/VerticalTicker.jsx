import React, { useState, useEffect } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

const VerticalTicker = ({ items = [], title = "LIVE DATA", type = "commodities" }) => {
  const [displayItems, setDisplayItems] = useState([]);

  useEffect(() => {
    // If we have items, duplicate them to ensure continuous scrolling
    if (items && items.length > 0) {
      // Create a longer list by duplicating items to ensure smooth continuous scrolling
      const extendedItems = [...items, ...items, ...items]; // Triple the items for smooth scrolling
      setDisplayItems(extendedItems);
    } else {
      setDisplayItems([]);
    }
  }, [items]);

  if (!items || items.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm h-64 flex items-center justify-center">
        <div className="text-center">
          <div className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-pulse mx-auto mb-2" />
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">NO {type.toUpperCase()} DATA</p>
        </div>
      </div>
    );
  }

  const formatPrice = (price) => {
    const num = Number(price);
    if (!Number.isFinite(num)) return "--";
    return num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
  };

  const ItemDisplay = ({ item, index }) => {
    if (!item) return null;

    // Handle different data structures for currencies/commodities vs stocks
    const change = Number(item.change_pct ?? item.change ?? item.percent_change ?? 0);
    const price = item.price ?? item.last_price ?? item.current_price ?? 0;
    const symbol = item.symbol ?? item.ticker ?? 'N/A';
    const exchange = item.exchange ?? 'FX'; // Default to FX for currencies
    const isUp = change >= 0;

    return (
      <div
        key={`item-${index}`}
        className="flex items-center justify-between p-3 rounded-lg border bg-slate-100 border-slate-200 mb-2 transition-all duration-300 last:mb-0"
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <div className="flex flex-col min-w-0">
            <span className="font-black text-slate-900 text-[10px] truncate">{symbol}</span>
            <span className="text-[8px] text-slate-500 uppercase">{exchange}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 min-w-fit">
          <span className="font-bold text-slate-800 text-[10px]">
            {type === 'currencies' ? '₹' : ''}{formatPrice(price)}
          </span>
          <div className={`flex items-center gap-1 ${isUp ? 'text-emerald-500' : 'text-red-500'}`}>
            {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
            <span className={`font-black text-[8px] ${isUp ? 'text-emerald-600' : 'text-red-600'}`}>
              {isUp ? '+' : ''}{change.toFixed(2)}%
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm h-64 flex flex-col overflow-hidden">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-heading font-black text-slate-900 text-sm">{title}</h3>
        <div className="flex items-center gap-1.5">
          <div className="h-1 w-1 rounded-full bg-green-500 animate-pulse" />
          <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">
            LIVE
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="h-full">
          <div className="vertical-ticker-content animate-vertical-ticker">
            {displayItems.map((item, index) => (
              <ItemDisplay key={`ticker-item-${index}`} item={item} index={index} />
            ))}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes vertical-ticker {
          0% { transform: translateY(100%); }
          100% { transform: translateY(-100%); }
        }
        .animate-vertical-ticker {
          animation: vertical-ticker 60s linear infinite;
          display: inline-block;
        }
      `}</style>
    </div>
  );
};

export default VerticalTicker;