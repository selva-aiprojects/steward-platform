import React, { useMemo } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";
import { useAppData } from "../context/AppDataContext";

export function MarketTicker() {
  const { marketMovers, loading } = useAppData() || {};

  const lanes = useMemo(() => {
    if (!marketMovers) return { nse: [], bse: [], mcx: [], metals: [] };

    const gainers = Array.isArray(marketMovers.gainers) ? marketMovers.gainers : [];
    const losers = Array.isArray(marketMovers.losers) ? marketMovers.losers : [];
    const all = [...gainers, ...losers].filter(
      (s) => s && s.symbol && s.exchange && Number.isFinite(Number(s.price))
    );

    const metalSet = new Set(["GOLD", "SILVER", "COPPER", "ALUMINIUM", "ZINC", "NICKEL"]);
    const isMetal = (sym = "") => metalSet.has(String(sym).toUpperCase());
    const ex = (e: any) => String(e || "").toUpperCase();

    const nse = all.filter((s) => ex(s.exchange) === "NSE");
    const bse = all.filter((s) => ex(s.exchange) === "BSE");
    const mcx = all.filter((s) => ex(s.exchange) === "MCX" && !isMetal(s.symbol));
    const metals = all.filter((s) => ex(s.exchange) === "MCX" && isMetal(s.symbol));

    const limit = (arr: any[]) => arr.slice(0, 24);

    return {
      nse: limit(nse),
      bse: limit(bse),
      mcx: limit(mcx),
      metals: limit(metals),
    };
  }, [marketMovers]);

  const exchangeClass = (exchange = "") => {
    switch (exchange.toUpperCase()) {
      case "NSE":
        return "text-emerald-400 border-emerald-500/40";
      case "BSE":
        return "text-sky-400 border-sky-500/40";
      case "MCX":
        return "text-amber-400 border-amber-500/40";
      default:
        return "text-slate-400 border-slate-500/40";
    }
  };

  const formatPrice = (price: any) => {
    const num = Number(price);
    if (!Number.isFinite(num)) return "--";
    return num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
  };

  if (loading) return null;

  const TickerItem = ({ item }: { item: any }) => {
    const change = Number(item.change_pct ?? item.change ?? 0);
    const isUp = change >= 0;

    return (
      <div className="flex items-center gap-4 bg-slate-800/60 backdrop-blur px-4 py-2 rounded-xl border border-slate-700/60 min-w-[200px] shadow-lg">
        <div className="flex flex-col">
          <span
            className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border ${exchangeClass(
              item.exchange
            )}`}
          >
            {item.exchange}
          </span>
          <span className="text-sm font-bold text-white">{item.symbol}</span>
        </div>

        <div className="flex flex-col items-end ml-auto">
          <span className="text-sm font-bold text-white">₹ {formatPrice(item.price)}</span>
          <div
            className={`flex items-center gap-1 text-xs font-semibold ${
              isUp ? "text-emerald-400" : "text-red-400"
            }`}
          >
            {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {isUp ? "+" : ""}
            {change.toFixed(2)}%
          </div>
        </div>
      </div>
    );
  };

  const Row = ({ label, items }: { label: string; items: any[] }) => {
    if (!items || items.length === 0) return null;
    return (
      <div className="pl-36 pr-6 py-2">
        <div className="flex flex-nowrap gap-6 animate-ticker whitespace-nowrap">
          <span className="text-[10px] font-bold text-white tracking-widest">{label}</span>
          {items.map((stock, i) => (
            <TickerItem key={label + stock.symbol + i} item={stock} />
          ))}
          {items.map((stock, i) => (
            <TickerItem key={label + stock.symbol + "-dup-" + i} item={stock} />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full bg-slate-950 border-b border-slate-800 relative overflow-hidden">
      <div className="absolute left-0 top-0 h-full px-5 flex items-center bg-slate-950 border-r border-slate-800 z-20">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] font-bold text-white tracking-widest">LIVE MARKET</span>
        </div>
      </div>
      <Row label="NSE" items={lanes.nse} />
      <Row label="BSE" items={lanes.bse} />
      <Row label="MCX" items={lanes.mcx} />
      <Row label="Metals" items={lanes.metals} />
    </div>
  );
}
