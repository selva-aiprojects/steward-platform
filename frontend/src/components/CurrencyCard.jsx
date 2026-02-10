import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const CurrencyCard = ({ currencies = [] }) => {
  if (!currencies || currencies.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-heading font-black text-slate-900 text-sm">Currency Rates</h3>
          <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
            FX PAIRS
          </span>
        </div>
        <div className="text-[10px] font-bold text-slate-400">No FX data</div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-heading font-black text-slate-900 text-sm">Currency Rates</h3>
        <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
          FX PAIRS
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {currencies.map((item, i) => {
          const change = Number(item.change || 0);
          const isUp = change >= 0;
          const price = Number(item.price);
          
          return (
            <div
              key={i}
              className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex justify-between items-center"
            >
              <div>
                <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border border-slate-300">
                  {item.symbol}
                </span>
              </div>
              <div className="text-right">
                <div className="text-[10px] font-bold">
                  {Number.isFinite(price) && price !== 0
                    ? price.toLocaleString('en-IN', { maximumFractionDigits: 4 })
                    : '--'}
                </div>
                <div className={`text-[9px] font-black ${isUp ? 'text-emerald-500' : 'text-red-500'}`}>
                  {isUp ? '+' : ''}{change.toFixed(2)}%
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CurrencyCard;