import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const CompactTicker = ({ stocks = [], title = "LIVE MARKET DATA", height = "h-[15px]" }) => {
  if (!stocks || stocks.length === 0) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-md p-0.5 overflow-hidden">
        <div className="flex items-center gap-0.5 mb-0.25">
          <span className="text-[6px] font-black text-slate-500 uppercase tracking-tighter px-0.5 py-0.25 bg-slate-100 rounded-sm">
            {title}
          </span>
          <div className="h-0.25 w-0.25 rounded-full bg-slate-400" />
        </div>
        <div className={`${height} flex items-center justify-center`}>
          <span className="text-[6px] text-slate-400">No live tickers</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-md p-0.5 overflow-hidden">
      <div className="flex items-center gap-0.5 mb-0.25">
        <span className="text-[6px] font-black text-slate-500 uppercase tracking-tighter px-0.5 py-0.25 bg-slate-100 rounded-sm">
          {title}
        </span>
        <div className="h-0.25 w-0.25 rounded-full bg-emerald-500 animate-pulse" />
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
                  <div key={`${stock.symbol}-${index}`} className="mx-1 flex items-center gap-0.5 border-r border-slate-200 pr-1 last:border-r-0">
                    <div className="flex items-center gap-0.25">
                      <span className="text-[6px] font-black text-slate-600">{stock.symbol}</span>
                      <span className="text-[5px] text-slate-400">{stock.exchange}</span>
                    </div>
                    <div className="flex items-center gap-0.25">
                      {isUp ? (
                        <TrendingUp size={5} className="text-emerald-500 flex-shrink-0" />
                      ) : (
                        <TrendingDown size={5} className="text-red-500 flex-shrink-0" />
                      )}
                      <span className={`text-[6px] font-black ${isUp ? 'text-emerald-600' : 'text-red-600'}`}>
                        {isUp ? '+' : ''}{Number.isFinite(change) ? change.toFixed(2) : '0.00'}%
                      </span>
                    </div>
                    <span className="text-[6px] font-bold text-slate-800">
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
          animation: compact-scroll 35s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default CompactTicker;