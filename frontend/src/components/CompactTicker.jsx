import React from 'react';
import { TrendingUp, TrendingDown, Zap } from 'lucide-react';

const CompactTicker = ({ stocks = [], title = "LIVE FEED", height = "h-[40px]" }) => {
  if (!stocks || stocks.length === 0) {
    return (
      <div className="bg-[#0a0f18] border border-white/5 rounded-lg p-1.5 overflow-hidden">
        <div className="flex items-center gap-1.5 mb-1 opacity-40">
          <Zap size={10} className="text-blue-500" />
          <span className="text-[9px] font-black text-slate-400 uppercase tracking-tighter">{title}</span>
        </div>
        <div className={`${height} flex items-center justify-center`}>
          <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest animate-pulse">Scanning Exchange...</span>
        </div>
      </div>
    );
  }

  // Duplicate for seamless scroll
  const displayStocks = [...stocks, ...stocks];

  return (
    <div className="bg-[#0a0f18] border border-white/10 rounded-lg p-2 overflow-hidden shadow-xl group">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <span className="text-[9px] font-black text-blue-400 uppercase tracking-tight px-1.5 py-0.5 bg-blue-500/10 rounded border border-blue-500/20">
            {title}
          </span>
          <div className="h-1 w-1 rounded-full bg-emerald-500 animate-pulse" />
        </div>
        <span className="text-[8px] font-bold text-slate-600 uppercase tracking-widest whitespace-nowrap">Auto-Sync Active</span>
      </div>

      <div className={`${height} relative flex items-center`}>
        <div className="flex animate-marquee-compact whitespace-nowrap items-center">
          {displayStocks.map((stock, index) => {
            const change = Number(stock.change || 0);
            const isUp = change >= 0;
            const price = Number(stock.price || 0);

            return (
              <div key={`c-${index}`} className="mx-4 flex items-center gap-3 border-r border-white/5 pr-4 last:border-r-0 group-hover:bg-white/5 transition-colors p-1 rounded">
                <div className="flex flex-col">
                  <span className="text-[11px] font-black text-white/90">{stock.symbol}</span>
                  <span className="text-[7px] text-slate-500 font-bold uppercase">{stock.exchange || 'NSE'}</span>
                </div>

                <div className="flex flex-col items-end">
                  <span className="text-[10px] font-bold text-slate-200 tabular-nums font-mono">
                    ₹{price.toLocaleString('en-IN', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
                  </span>
                  <div className={`flex items-center gap-0.5 ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                    <span className="text-[9px] font-black tabular-nums tracking-tighter">
                      {isUp ? '+' : ''}{change.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        @keyframes marquee-compact {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee-compact {
          animation: marquee-compact 30s linear infinite;
        }
        .animate-marquee-compact:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};

export default CompactTicker;