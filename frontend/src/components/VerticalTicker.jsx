import React, { useState, useEffect, useMemo } from "react";
import { TrendingUp, TrendingDown, Clock, Activity } from "lucide-react";

/**
 * VerticalTicker - A high-standard trading terminal style vertical scroller
 */
const VerticalTicker = ({ items = [], title = "LIVE DATA", type = "commodities" }) => {

  const displayItems = useMemo(() => {
    if (!items || items.length === 0) return [];
    // Triple elements for seamless vertical loop
    return [...items, ...items, ...items];
  }, [items]);

  const formatPrice = (price) => {
    const num = Number(price);
    if (!Number.isFinite(num)) return "--";
    return num.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  if (!items || items.length === 0) {
    return (
      <div className="bg-[#0a0f18] border border-white/5 rounded-xl p-4 shadow-xl h-64 flex items-center justify-center">
        <div className="text-center opacity-40">
          <Activity size={24} className="text-blue-500 animate-pulse mx-auto mb-2" />
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">NO {type.toUpperCase()} DATA</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#0a0f18] border border-white/10 rounded-xl p-4 shadow-2xl h-[400px] flex flex-col overflow-hidden relative group">
      {/* Header Segment */}
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-white/5">
        <div className="flex flex-col">
          <h3 className="font-black text-white/90 text-xs uppercase tracking-tight flex items-center gap-1.5">
            {title}
          </h3>
          <span className="text-[8px] text-slate-500 font-bold uppercase tracking-widest">Real-time Stream</span>
        </div>
        <div className="flex items-center gap-1 bg-emerald-500/10 px-1.5 py-0.5 rounded">
          <div className="h-1 w-1 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[8px] font-black text-emerald-400 uppercase tracking-tighter">LIVE</span>
        </div>
      </div>

      <div className="flex-1 overflow-hidden relative">
        <div className="absolute inset-0 flex flex-col ticker-v-container">
          <div className="animate-vertical-loop flex flex-col">
            {displayItems.map((item, index) => {
              const change = Number(item.change_pct ?? item.change ?? 0);
              const price = item.price ?? item.last_price ?? 0;
              const symbol = item.symbol ?? 'N/A';
              const isUp = change >= 0;

              return (
                <div
                  key={`v-${index}`}
                  className="flex items-center justify-between p-2.5 rounded-lg border border-transparent hover:border-white/5 hover:bg-white/5 transition-all mb-1 cursor-default group/item"
                >
                  <div className="flex flex-col">
                    <span className="font-black text-white/80 text-[11px] group-hover/item:text-blue-400 transition-colors">{symbol}</span>
                    <span className="text-[8px] text-slate-600 font-bold uppercase">{item.exchange || 'MCX'}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex flex-col items-end">
                      <span className="font-bold text-slate-200 text-[10px] tabular-nums font-mono">
                        {type === 'currencies' ? '₹' : ''}{formatPrice(price)}
                      </span>
                      <div className={`flex items-center gap-0.5 ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                        <span className="text-[9px] font-black tabular-nums tracking-tighter">
                          {isUp ? '+' : ''}{change.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                    <div className={`w-1 h-6 rounded-full ${isUp ? 'bg-emerald-500/40' : 'bg-rose-500/40'}`} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer Meta */}
      <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between opacity-50">
        <div className="flex items-center gap-1">
          <Clock size={10} className="text-slate-500" />
          <span className="text-[8px] font-bold text-slate-500">Node: SS-ASIA-01</span>
        </div>
        <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest">Trading Hub Std</span>
      </div>

      <style>{`
        @keyframes vertical-loop {
          0% { transform: translateY(0); }
          100% { transform: translateY(-33.33%); }
        }
        .animate-vertical-loop {
          animation: vertical-loop 30s linear infinite;
        }
        .animate-vertical-loop:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};

export default VerticalTicker;
