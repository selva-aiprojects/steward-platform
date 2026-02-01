import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card } from "../components/ui/card";
import { Briefcase, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const mockHoldings = [
  { symbol: 'AAPL', quantity: 10, avgPrice: 175.50, currentPrice: 182.30, pnl: 68.00, pnlPct: 3.87 },
  { symbol: 'TSLA', quantity: 5, avgPrice: 240.20, currentPrice: 235.10, pnl: -25.50, pnlPct: -2.12 },
  { symbol: 'MSFT', quantity: 15, avgPrice: 380.00, currentPrice: 405.20, pnl: 378.00, pnlPct: 6.63 },
  { symbol: 'NIFTY50', quantity: 100, avgPrice: 2200.00, currentPrice: 2250.40, pnl: 5040.00, pnlPct: 2.29 },
];

const allocationData = [
  { name: 'Technology', value: 65 },
  { name: 'Automotive', value: 15 },
  { name: 'Index Funds', value: 20 },
];

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

const Portfolio: React.FC = () => {
  const [isTradeModalOpen, setIsTradeModalOpen] = React.useState(false);
  const [selectedSymbol, setSelectedSymbol] = React.useState('AAPL');

  return (
    <div className="portfolio-container pb-20">
      <header className="page-header flex justify-between items-end">
        <div>
          <div className="header-eyebrow">
            <span className="badge-virtual">VIRTUAL HOLDINGS</span>
          </div>
          <h1>Simulated Portfolio</h1>
          <p>Detailed breakdown of your virtual assets and positions.</p>
        </div>
        <button
          onClick={() => setIsTradeModalOpen(true)}
          className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 transition-all shadow-lg shadow-primary/20"
        >
          <ArrowUpRight size={18} />
          Execute Manual Trade
        </button>
      </header>

      {/* Manual Trade Modal Override */}
      {isTradeModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border w-full max-w-md rounded-2xl shadow-2xl p-6 relative animate-in zoom-in duration-200">
            <button
              onClick={() => setIsTradeModalOpen(false)}
              className="absolute right-4 top-4 text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
            <h2 className="text-xl font-bold mb-1">Manual Trade Terminal</h2>
            <p className="text-xs text-muted-foreground mb-6">User Override: Bypassing AI Steward logic.</p>

            <div className="space-y-4">
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Select Ticker</label>
                <select
                  value={selectedSymbol}
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                  className="w-full mt-1 bg-muted/50 border rounded-lg p-3 text-sm font-bold focus:ring-2 focus:ring-primary outline-none"
                >
                  <option>AAPL</option>
                  <option>NVDA</option>
                  <option>TSLA</option>
                  <option>AMD</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <button className="py-4 rounded-xl bg-green-500 text-white font-black text-sm hover:bg-green-600 transition-colors">BUY</button>
                <button className="py-4 rounded-xl bg-red-500 text-white font-black text-sm hover:bg-red-600 transition-colors">SELL</button>
              </div>

              <button
                className="w-full py-3 rounded-xl border-2 border-dashed border-muted-foreground/30 text-muted-foreground font-bold text-xs hover:bg-muted/10"
                onClick={() => setIsTradeModalOpen(false)}
              >
                Cancel and Let Agent Decide
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-8">
        <Card className="lg:col-span-8 p-0 border-slate-100 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-50 flex items-center gap-3">
            <Briefcase size={20} className="text-primary" />
            <h2 className="font-black text-slate-900 uppercase text-sm tracking-widest">Current Holdings</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="text-[10px] font-black text-slate-400 uppercase tracking-widest border-b bg-slate-50/50">
                  <th className="px-6 py-4">Symbol</th>
                  <th className="px-6 py-4">Qty</th>
                  <th className="px-6 py-4">Avg Price</th>
                  <th className="px-6 py-4">Current</th>
                  <th className="px-6 py-4">PnL</th>
                  <th className="px-6 py-4 text-right">Change</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {mockHoldings.map((holding) => (
                  <tr key={holding.symbol} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-5 font-black text-slate-900">{holding.symbol}</td>
                    <td className="px-6 py-5 font-medium text-slate-600">{holding.quantity}</td>
                    <td className="px-6 py-5 font-medium text-slate-600">${holding.avgPrice.toFixed(2)}</td>
                    <td className="px-6 py-5 font-medium text-slate-600">${holding.currentPrice.toFixed(2)}</td>
                    <td className={`px-6 py-5 font-bold ${holding.pnl >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                      {holding.pnl >= 0 ? '+' : ''}${Math.abs(holding.pnl).toFixed(2)}
                    </td>
                    <td className="px-6 py-5 text-right">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-black ${holding.pnlPct >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'
                        }`}>
                        {holding.pnlPct >= 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                        {Math.abs(holding.pnlPct)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="lg:col-span-4 p-8 border-slate-100 shadow-sm">
          <h2 className="font-black text-slate-900 uppercase text-xs tracking-widest mb-8">Asset Allocation</h2>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={8}
                  dataKey="value"
                  stroke="none"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" align="center" iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <footer className="mt-12 p-8 rounded-2xl bg-slate-50 border border-slate-100">
        <p className="text-[11px] text-slate-500 leading-relaxed font-medium">
          <strong className="text-slate-900 font-black uppercase tracking-widest mr-2">Compliance Disclaimer:</strong>
          StockSteward AI provides a simulated trading environment. The data displayed here does not represent real financial transactions. No guarantee of profits is implied or provided. Independent financial advice should be sought before engaging in real-market activities. All trade signals are generated for educational purposes.
        </p>
      </footer>
    </div>
  );
};

export default Portfolio;
