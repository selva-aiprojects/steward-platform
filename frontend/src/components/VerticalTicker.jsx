import React, { useState, useEffect } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

const VerticalTicker = ({ items = [], title = "LIVE DATA", type = "commodities" }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (items.length <= 1) return; // Don't animate if there's only one item or none
    
    const interval = setInterval(() => {
      setCurrentIndex(prevIndex => (prevIndex + 1) % items.length);
    }, 3000); // Change item every 3 seconds

    return () => clearInterval(interval);
  }, [items.length]);

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

  // Get 3 items to show: current, next, and one more ahead
  const getItem = (offset) => {
    if (items.length === 0) return null;
    const index = (currentIndex + offset) % items.length;
    return items[index];
  };

  const currentItem = getItem(0);
  const nextItem = getItem(1);
  const thirdItem = getItem(2);

  const formatPrice = (price) => {
    const num = Number(price);
    if (!Number.isFinite(num)) return "--";
    return num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
  };

  const ItemDisplay = ({ item, isNext = false }) => {
    if (!item) return null;
    
    const change = Number(item.change_pct ?? item.change ?? 0);
    const isUp = change >= 0;

    return (
      <div className={`flex items-center justify-between p-3 rounded-lg border ${isNext ? 'bg-slate-50 border-slate-100' : 'bg-slate-100 border-slate-200'} transition-all duration-500`}>
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <div className="flex flex-col min-w-0">
            <span className="font-black text-slate-900 text-[10px] truncate">{item.symbol}</span>
            {item.exchange && (
              <span className="text-[8px] text-slate-500 uppercase">{item.exchange}</span>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2 min-w-fit">
          <span className="font-bold text-slate-800 text-[10px]">
            {type === 'currencies' ? '₹' : ''}{formatPrice(item.price)}
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
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm h-64 flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-heading font-black text-slate-900 text-sm">{title}</h3>
        <div className="flex items-center gap-1.5">
          <div className="h-1 w-1 rounded-full bg-green-500 animate-pulse" />
          <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">
            LIVE
          </span>
        </div>
      </div>
      
      <div className="flex-1 flex flex-col justify-center space-y-2">
        {currentItem && <ItemDisplay item={currentItem} isNext={false} />}
        {nextItem && <ItemDisplay item={nextItem} isNext={true} />}
        {thirdItem && <ItemDisplay item={thirdItem} isNext={true} />}
      </div>
      
      <div className="mt-auto pt-3 flex justify-center">
        <div className="flex gap-1">
          {items.map((_, idx) => (
            <div
              key={idx}
              className={`h-0.5 w-2.5 rounded-full transition-all ${
                idx === currentIndex ? 'bg-primary' : 'bg-slate-200'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default VerticalTicker;