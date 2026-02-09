import React, { useMemo } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

export default function SlimLiveTicker({
                                           data = [],
                                           title = "LIVE MARKET",
                                           height = "h-10"
                                       }) {

    const items = useMemo(() => {
        return data
            .filter(d => d && d.symbol && Number.isFinite(Number(d.price || d.ltp)))
            .map(d => ({
                symbol: d.symbol,
                price: Number(d.price ?? d.ltp),
                change: Number(d.change ?? 0)
            }));
    }, [data]);

    if (!items.length) return null;

    return (
        <div className={`w-full ${height} bg-slate-950 border-y border-slate-800 overflow-hidden relative`}>

            {/* Left Title */}
            <div className="absolute left-0 top-0 bottom-0 z-20 flex items-center px-4 bg-gradient-to-r from-slate-950 via-slate-950 to-transparent">
        <span className="text-[10px] font-black tracking-widest text-primary">
          {title}
        </span>
            </div>

            {/* Scrolling Ticker */}
            <div className="flex h-full items-center animate-marquee whitespace-nowrap pl-40">

                {items.concat(items).map((item, i) => {
                    const isUp = item.change >= 0;

                    return (
                        <div
                            key={i}
                            className="flex items-center gap-2 px-6 text-xs font-bold"
                        >
                            <span className="text-slate-300">{item.symbol}</span>

                            <span className="text-white">
                ₹ {item.price.toLocaleString("en-IN")}
              </span>

                            <span className={isUp ? "text-emerald-400" : "text-red-400"}>
                {isUp ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
              </span>

                            <span className={isUp ? "text-emerald-400" : "text-red-400"}>
                {isUp ? "+" : ""}
                                {item.change.toFixed(2)}%
              </span>
                        </div>
                    );
                })}
            </div>

            {/* CSS */}
            <style jsx>{`
        .animate-marquee {
          animation: marquee 35s linear infinite;
        }

        @keyframes marquee {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }
      `}</style>
        </div>
    );
}
