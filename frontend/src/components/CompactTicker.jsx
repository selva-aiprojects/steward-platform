import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const CompactTicker = ({ stocks = [], title = "LIVE MARKET DATA", height = "h-[40px]" }) => {
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
          <span className="text-[8px] text-slate-400">No live tickers</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-md p-0.5 overflow-hidden">
      <div className="flex items-center gap-0.5 mb-0.25">
        <span className="text-[8px] font-black text-slate-500 uppercase tracking-tight px-1 py-0.5 bg-slate-100 rounded-sm">
          {title}
        </span>
        <div className="h-0.25 w-0.25 rounded-full bg-emerald-500 animate-pulse" />
      </div>
      <div className={`${height}`}>
        <div className="h-full overflow-hidden">
          <div className="h-full flex items-center">
            <div className="flex animate-compact-scroll-loop whitespace-nowrap h-full items-center">
              {/* First set of stocks */}
              {stocks.map((stock, index) => {
                const change = Number(stock.change || 0);
                const isUp = change >= 0;
                const price = Number(stock.price || 0);

                return (
                  <div key={`ticker-${stock.symbol}-${index}`} className="mx-2 flex items-center gap-1 border-r border-slate-200 pr-2 last:border-r-0 min-w-[140px]">
                    <div className="flex items-center gap-0.5">
                      <span className="text-[9px] font-black text-slate-600">{stock.symbol}</span>
                      <span className="text-[7px] text-slate-400">{stock.exchange}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      {isUp ? (
                        <TrendingUp size={8} className="text-emerald-500 flex-shrink-0" />
                      ) : (
                        <TrendingDown size={8} className="text-red-500 flex-shrink-0" />
                      )}
                      <span className={`text-[8px] font-black ${isUp ? 'text-emerald-600' : 'text-red-600'}`}>
                        {isUp ? '+' : ''}{Number.isFinite(change) ? change.toFixed(2) : '0.00'}%
                      </span>
                    </div>
                    <span className="text-[9px] font-bold text-slate-800">
                      {Number.isFinite(price) && price !== 0
                        ? `₹${price.toLocaleString('en-IN', { maximumFractionDigits: 1 })}`
                        : 'N/A'}
                    </span>
                  </div>
                );
              })}
              {/* Duplicate set for seamless loop */}
              {stocks.map((stock, index) => {
                const change = Number(stock.change || 0);
                const isUp = change >= 0;
                const price = Number(stock.price || 0);

                return (
                  <div key={`ticker-duplicate-${stock.symbol}-${index}`} className="mx-2 flex items-center gap-1 border-r border-slate-200 pr-2 last:border-r-0 min-w-[140px]">
                    <div className="flex items-center gap-0.5">
                      <span className="text-[9px] font-black text-slate-600">{stock.symbol}</span>
                      <span className="text-[7px] text-slate-400">{stock.exchange}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      {isUp ? (
                        <TrendingUp size={8} className="text-emerald-500 flex-shrink-0" />
                      ) : (
                        <TrendingDown size={8} className="text-red-500 flex-shrink-0" />
                      )}
                      <span className={`text-[8px] font-black ${isUp ? 'text-emerald-600' : 'text-red-600'}`}>
                        {isUp ? '+' : ''}{Number.isFinite(change) ? change.toFixed(2) : '0.00'}%
                      </span>
                    </div>
                    <span className="text-[9px] font-bold text-slate-800">
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
        @keyframes compact-scroll-loop {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
        .animate-compact-scroll-loop {
          animation: compact-scroll-loop 60s linear infinite;
          display: inline-flex;
          height: 100%;
        }
      `}</style>
    </div>
  );
};

export default CompactTicker;