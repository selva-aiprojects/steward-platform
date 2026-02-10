import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const CompactTicker = ({ stocks = [], title = "LIVE MARKET DATA", height = "h-10" }) => {
  if (!stocks || stocks.length === 0) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-1.5 overflow-hidden">
        <div className="flex items-center gap-1.5 mb-1">
          <span className="text-[9px] font-black text-slate-500 uppercase tracking-wider px-1.5 py-0.5 bg-slate-100 rounded">
            {title}
          </span>
          <div className="h-1 w-1 rounded-full bg-slate-400" />
        </div>
        <div className={`${height} flex items-center justify-center`}>
          <span className="text-[9px] text-slate-400">No live tickers</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-1.5 overflow-hidden">
      <div className="flex items-center gap-1.5 mb-1">
        <span className="text-[9px] font-black text-slate-500 uppercase tracking-wider px-1.5 py-0.5 bg-slate-100 rounded">
          {title}
        </span>
        <div className="h-1 w-1 rounded-full bg-emerald-500 animate-pulse" />
      </div>
      <div className={`${height}`}>
        <div className="h-full ticker-container">
          <div className="h-full flex items-center">
            <div className="flex animate-compact-scroll whitespace-nowrap w-max">
              {stocks.map((stock, index) => {
                const change = Number(stock.change || 0);
                const isUp = change >= 0;
                const price = Number(stock.price || 0);

                return (
                  <div key={`${stock.symbol}-${index}`} className="mx-2 flex items-center gap-1.5 border-r border-slate-200 pr-2 last:border-r-0">
                    <div className="flex items-center gap-0.5">
                      <span className="text-[9px] font-black text-slate-600">{stock.symbol}</span>
                      <span className="text-[7px] text-slate-400">{stock.exchange}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      {isUp ? (
                        <TrendingUp size={9} className="text-emerald-500 flex-shrink-0" />
                      ) : (
                        <TrendingDown size={9} className="text-red-500 flex-shrink-0" />
                      )}
                      <span className={`text-[8px] font-black ${isUp ? 'text-emerald-600' : 'text-red-600'}`}>
                        {isUp ? '+' : ''}{Number.isFinite(change) ? change.toFixed(2) : '0.00'}%
                      </span>
                    </div>
                    <span className="text-[8px] font-bold text-slate-800">
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

      <style jsx>{`
        @keyframes compact-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-compact-scroll {
          animation: compact-scroll 45s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default CompactTicker;