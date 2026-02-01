import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Card } from "../components/ui/card";
import { useNavigate, Link } from "react-router-dom";
import { Briefcase, ArrowUpRight, ArrowDownRight, GripVertical, Lock, ShieldCheck, Database, Award, Plus, Trash2 } from 'lucide-react';
import { useUser } from '../context/UserContext';

const mockHoldingsInit = [
  { id: '1', symbol: 'AAPL', quantity: 10, avgPrice: 175.50, currentPrice: 182.30, pnl: 68.00, pnlPct: 3.87, type: 'active' },
  { id: '2', symbol: 'TSLA', quantity: 5, avgPrice: 240.20, currentPrice: 235.10, pnl: -25.50, pnlPct: -2.12, type: 'active' },
  { id: '3', symbol: 'MSFT', quantity: 15, avgPrice: 380.00, currentPrice: 405.20, pnl: 378.00, pnlPct: 6.63, type: 'active' },
];

const mockWatchlistInit = [
  { id: '4', symbol: 'NVDA', currentPrice: 460.10, change: '+1.2%', type: 'watch' },
  { id: '5', symbol: 'AMD', currentPrice: 105.25, change: '+0.8%', type: 'watch' },
  { id: '6', symbol: 'AMZN', currentPrice: 135.00, change: '-0.5%', type: 'watch' },
  { id: '7', symbol: 'GOOGL', currentPrice: 138.50, change: '+0.2%', type: 'watch' },
];

const wealthProjection = [
  { year: '2024', conservative: 100000, aggressive: 100000 },
  { year: '2025', conservative: 112000, aggressive: 125000 },
  { year: '2026', conservative: 125440, aggressive: 156250 },
  { year: '2027', conservative: 140490, aggressive: 195300 },
  { year: '2028', conservative: 157350, aggressive: 244100 },
];

const allocationData = [
  { name: 'Technology', value: 65 },
  { name: 'Automotive', value: 15 },
  { name: 'Index Funds', value: 20 },
];

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

const Portfolio = () => {
  const { user } = useUser();
  const [activeHoldings, setActiveHoldings] = useState(mockHoldingsInit);
  const [watchlist, setWatchlist] = useState(mockWatchlistInit);
  const [draggedItem, setDraggedItem] = useState(null);

  const isManual = user?.trading_mode === 'MANUAL';

  const handleDragStart = (e, item) => {
    if (!isManual) return;
    setDraggedItem(item);
    e.dataTransfer.effectAllowed = 'move';
    // Visual drag image enhancement could go here
  };

  const handleDragOver = (e) => {
    if (!isManual) return;
    e.preventDefault();
  };

  const handleDrop = (e, targetSection) => {
    if (!isManual || !draggedItem) return;
    e.preventDefault();

    if (targetSection === 'active' && draggedItem.type === 'watch') {
      setWatchlist(watchlist.filter(i => i.id !== draggedItem.id));
      setActiveHoldings([...activeHoldings, { ...draggedItem, type: 'active', quantity: 1, avgPrice: draggedItem.currentPrice, pnl: 0, pnlPct: 0 }]); // Add default quantity logic
    } else if (targetSection === 'watch' && draggedItem.type === 'active') {
      setActiveHoldings(activeHoldings.filter(i => i.id !== draggedItem.id));
      setWatchlist([...watchlist, { ...draggedItem, type: 'watch', change: '0.0%' }]);
    }
    setDraggedItem(null);
  };

  return (
    <div className="portfolio-container pb-20 space-y-8 animate-in fade-in duration-500">
      <header className="page-header flex justify-between items-end">
        <div>
          <div className="header-eyebrow flex items-center gap-2">
            <span className="badge-virtual">VIRTUAL HOLDINGS</span>
            {!isManual && <span className="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-black flex items-center gap-1"><Lock size={10} /> AUTO-MANAGED</span>}
          </div>
          <h1 className="text-3xl font-black text-slate-900">Wealth Allocation</h1>
          <p className="text-slate-500 font-medium text-sm">Interactive portfolio composition and wealth projection.</p>
        </div>
      </header>

      {/* Interactive Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* Active Allocation Zone */}
        <Card
          className={`p-6 border-2 border-dashed transition-all ${isManual ? 'border-primary/20 bg-primary/5' : 'border-slate-100 bg-slate-50 opacity-80'}`}
          onDragOver={handleDragOver}
          onDrop={(e) => handleDrop(e, 'active')}
        >
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="font-black text-slate-900 uppercase tracking-widest text-sm flex items-center gap-2">
                <Briefcase size={16} /> Active Allocation
              </h3>
              <p className="text-[10px] text-slate-500 font-bold mt-1">
                {isManual ? "Drag stocks here to allocate capital." : "Managed by Steward AI"}
              </p>
            </div>
            {!isManual && <Lock className="text-slate-400" size={20} />}
          </div>

          <div className="space-y-3 min-h-[200px]">
            {activeHoldings.map((stock) => (
              <Link to="/trading" key={stock.id} className="block">
                <div
                  draggable={isManual}
                  onDragStart={(e) => handleDragStart(e, stock)}
                  className={`bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-primary/40 hover:shadow-md transition-all ${isManual ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'}`}
                >
                  <div className="flex items-center gap-3">
                    {isManual && <GripVertical className="text-slate-300" size={16} />}
                    <div className="h-8 w-8 rounded-lg bg-slate-100 flex items-center justify-center font-black text-[10px] text-slate-700 group-hover:bg-primary/10 group-hover:text-primary transition-colors">{stock.symbol.substring(0, 1)}</div>
                    <div>
                      <p className="font-black text-slate-900 text-sm group-hover:text-primary transition-colors">{stock.symbol}</p>
                      <p className="text-[10px] text-slate-500 font-mono">${stock.currentPrice.toFixed(2)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-black ${stock.pnlPct >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                      {stock.pnlPct >= 0 ? '+' : ''}{stock.pnlPct}%
                    </p>
                    <p className="text-[10px] text-slate-400 font-bold uppercase">PnL</p>
                  </div>
                </div>
              </Link>
            ))}
            {activeHoldings.length === 0 && (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs font-medium border-2 border-dashed border-slate-200 rounded-xl p-8">
                No active assets. Drag from watchlist to fund.
              </div>
            )}
          </div>
        </Card>

        {/* Watchlist / Market Zone */}
        <Card
          className="p-6 border-slate-100 bg-white"
          onDragOver={handleDragOver}
          onDrop={(e) => handleDrop(e, 'watch')}
        >
          <h3 className="font-black text-slate-900 uppercase tracking-widest text-sm mb-6 flex items-center gap-2">
            <Database size={16} /> Market Opportunities
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {watchlist.map((stock) => (
              <Link to="/trading" key={stock.id}>
                <div
                  draggable={isManual}
                  onDragStart={(e) => handleDragStart(e, stock)}
                  className={`p-4 bg-slate-50 rounded-xl border border-slate-100 flex flex-col justify-between h-24 group hover:bg-white hover:border-primary/30 hover:shadow-md transition-all ${isManual ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-black text-slate-900 group-hover:text-primary transition-colors">{stock.symbol}</span>
                    {isManual && <GripVertical className="text-slate-300" size={12} />}
                  </div>
                  <p className="text-[10px] text-slate-400 font-mono">${stock.currentPrice.toFixed(2)}</p>
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-8 p-4 bg-indigo-50 rounded-xl border border-indigo-100">
            <h4 className="text-indigo-900 font-black text-xs uppercase tracking-widest mb-2">AI Insight</h4>
            <p className="text-[11px] text-indigo-700 leading-relaxed font-medium">
              Sector rotation suggests moving 15% allocation from <strong>Automotive</strong> to <strong>Semiconductors</strong> based on recent supply chain analysis.
            </p>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Wealth Projection Chart */}
        <Card className="lg:col-span-8 p-8 border-slate-100 shadow-sm">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="font-black text-slate-900 uppercase text-xs tracking-widest">Retirement Wealth Projection</h2>
              <p className="text-xs text-slate-400 font-medium mt-1">Estimated compound growth triggers based on current allocation.</p>
            </div>
            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                <span className="text-[10px] font-bold text-slate-600 uppercase">Aggressive</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-indigo-500" />
                <span className="text-[10px] font-bold text-slate-600 uppercase">Conservative</span>
              </div>
            </div>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={wealthProjection}>
                <defs>
                  <linearGradient id="colorAgg" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorCons" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="year" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} tickFormatter={(val) => `$${val / 1000}k`} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                <Area type="monotone" dataKey="aggressive" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorAgg)" />
                <Area type="monotone" dataKey="conservative" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorCons)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Allocation Pie Chart */}
        <Card className="lg:col-span-4 p-8 border-slate-100 shadow-sm flex flex-col justify-center">
          <h2 className="font-black text-slate-900 uppercase text-xs tracking-widest mb-4">Current Risk Exposure</h2>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" align="center" iconType="circle" wrapperStyle={{ fontSize: '10px', fontWeight: '700' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Trust & Security Footer - Enterprise Grade */}
      <footer className="mt-12 p-8 rounded-2xl bg-slate-900 border border-slate-800 text-slate-400">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/5 rounded-lg text-emerald-400">
              <ShieldCheck size={24} />
            </div>
            <div>
              <h4 className="text-white font-black text-xs uppercase tracking-widest">SOC2 Type II</h4>
              <p className="text-[10px] opacity-70">Audited Compliance</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/5 rounded-lg text-blue-400">
              <Lock size={24} />
            </div>
            <div>
              <h4 className="text-white font-black text-xs uppercase tracking-widest">AES-256</h4>
              <p className="text-[10px] opacity-70">Bank-Grade Encryption</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/5 rounded-lg text-amber-400">
              <Database size={24} />
            </div>
            <div>
              <h4 className="text-white font-black text-xs uppercase tracking-widest">Redundant Data</h4>
              <p className="text-[10px] opacity-70">Multi-Region Backup</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/5 rounded-lg text-purple-400">
              <Award size={24} />
            </div>
            <div>
              <h4 className="text-white font-black text-xs uppercase tracking-widest">SEC Regulated</h4>
              <p className="text-[10px] opacity-70">Registered Advisor</p>
            </div>
          </div>
        </div>
        <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-[10px] leading-relaxed font-medium">
            <strong className="text-white font-black uppercase tracking-widest mr-2">Disclaimer:</strong>
            StockSteward AI is a registered investment advisor. Past performance is not indicative of future results. All investments involve risk, including the loss of principal.
          </p>
          <p className="text-[10px] font-mono opacity-50">v2.4.0-Enterprise</p>
        </div>
      </footer>
    </div>
  );
};

export default Portfolio;
