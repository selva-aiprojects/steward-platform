import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const CompactTicker = ({ stocks = [], title = "LIVE MARKET DATA", height = "h-12" }) => {
  if (!stocks || stocks.length === 0) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-2 overflow-hidden">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-2 py-1 bg-slate-100 rounded-lg">
            {title}
          </span>
          <div className="h-1.5 w-1.5 rounded-full bg-slate-400" />
        </div>
        <div className={`${height} flex items-center justify-center`}>
          <span className="text-xs text-slate-400">No live tickers available</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-2 overflow-hidden">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-2 py-1 bg-slate-100 rounded-lg">
          {title}
        </span>
        <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
      </div>
      <div className={`${height}`}>
        <div className="h-full ticker-container">
          <div className="h-full flex items-center">
            <div className="flex animate-scroll whitespace-nowrap w-max">
              {stocks.map((stock, index) => {
                const change = Number(stock.change || 0);
                const isUp = change >= 0;
                const price = Number(stock.price);

                return (
                  <div key={`${stock.symbol}-${index}`} className="mx-3 flex items-center gap-3 border-r border-slate-200 pr-3 last:border-r-0">
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-black text-slate-600">{stock.symbol}</span>
                      <span className="text-[8px] text-slate-400">{stock.exchange}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      {isUp ? (
                        <TrendingUp size={12} className="text-emerald-500 flex-shrink-0" />
                      ) : (
                        <TrendingDown size={12} className="text-red-500 flex-shrink-0" />
                      )}
                      <span className={`text-xs font-black ${isUp ? 'text-emerald-600' : 'text-red-600'}`}>
                        {isUp ? '+' : ''}{Number.isFinite(change) ? change.toFixed(2) : '0.00'}%
                      </span>
                    </div>
                    <span className="text-xs font-bold text-slate-800">
                      {Number.isFinite(price) && price !== 0
                        ? `₹${price.toLocaleString('en-IN', { maximumFractionDigits: 1 })}`
                        : 'N/A'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompactTicker;