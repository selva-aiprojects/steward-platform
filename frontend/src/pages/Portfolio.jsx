import React, { useState, useEffect } from 'react';
import {
  ArrowUpRight, ArrowDownRight, TrendingUp, TrendingDown,
  DollarSign, Activity, PieChart as PieChartIcon, Target,
  Shield, Zap, RefreshCcw, Loader2, Plus, GripVertical, X
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { Card } from "../components/ui/card";
import { useNavigate, Link } from "react-router-dom";
import { fetchPortfolioHistory, depositFunds, withdrawFunds, addToWatchlist, removeFromWatchlist } from "../services/api";
import { useUser } from '../context/UserContext';
import { useAppData } from '../context/AppDataContext';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const Portfolio = () => {
  const { user, selectedUser } = useUser();
  const {
    summary,
    holdings: activeHoldings,
    watchlist: appWatchlist,
    projections,
    stewardPrediction: appStewardPrediction,
    loading,
    refreshAllData
  } = useAppData();

  const [watchlist, setWatchlist] = useState([]);
  const [history, setHistory] = useState([]);
  const [depositing, setDepositing] = useState(false);
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [depositAmount, setDepositAmount] = useState(5000);
  const [withdrawing, setWithdrawing] = useState(false);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState(2000);
  const [fundStatus, setFundStatus] = useState(null);
  const [draggedItem, setDraggedItem] = useState(null);

  const viewId = selectedUser?.id || user?.id;
  const isManual = user?.trading_mode === 'MANUAL';

  useEffect(() => {
    if (appWatchlist) setWatchlist(appWatchlist);
  }, [appWatchlist]);

  useEffect(() => {
    const loadHistory = async () => {
      if (!viewId) return;
      try {
        const historyData = await fetchPortfolioHistory(viewId);
        setHistory(Array.isArray(historyData) ? historyData : []);
      } catch (err) {
        console.error("History Load Error:", err);
      }
    };
    loadHistory();
  }, [viewId]);

  const handleDeposit = async () => {
    if (!viewId || depositAmount <= 0) return;
    setDepositing(true);
    try {
      const result = await depositFunds(viewId, depositAmount);
      if (result) {
        await refreshAllData();
        setShowDepositModal(false);
        setFundStatus({ type: 'success', msg: `Deposit completed: INR ${depositAmount.toLocaleString()}` });
        alert(`Successfully deposited INR ${depositAmount.toLocaleString()} into your vault.`);
      }
    } catch (err) {
      console.error("Deposit failed:", err);
      setFundStatus({ type: 'error', msg: 'Deposit failed. Please retry.' });
    } finally {
      setDepositing(false);
    }
  };

  const handleWithdraw = async () => {
    if (!viewId || withdrawAmount <= 0) return;
    setWithdrawing(true);
    try {
      const result = await withdrawFunds(viewId, withdrawAmount);
      if (result) {
        await refreshAllData();
        setShowWithdrawModal(false);
        setFundStatus({ type: 'success', msg: `Withdraw completed: INR ${withdrawAmount.toLocaleString()}` });
        alert(`Successfully withdrew INR ${withdrawAmount.toLocaleString()} from your vault.`);
      }
    } catch (err) {
      console.error("Withdraw failed:", err);
      setFundStatus({ type: 'error', msg: 'Withdraw failed. Please retry.' });
    } finally {
      setWithdrawing(false);
    }
  };

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

  const handleDrop = async (e, targetSection) => {
    if (!isManual || !draggedItem) return;
    e.preventDefault();

    try {
      if (targetSection === 'active' && draggedItem.type === 'watch') {
        // For demo: remove from watchlist and let refresh hydrate holdings
        setWatchlist(watchlist.filter(i => i.id !== draggedItem.id));
        await removeFromWatchlist(viewId, draggedItem.symbol);
      } else if (targetSection === 'watch' && draggedItem.type === 'active') {
        setWatchlist([...watchlist, { ...draggedItem, type: 'watch', change: '0.0%' }]);
        await addToWatchlist(viewId, draggedItem.symbol);
      }
      await refreshAllData();
    } catch (err) {
      console.error("Drop persistence failed:", err);
    }
    setDraggedItem(null);
  };

  const allocationData = activeHoldings.length > 0 ? activeHoldings.map(h => {
    const price = h.current_price ?? h.currentPrice ?? 0;
    return {
      name: h.symbol,
      value: h.quantity * price
    };
  }) : [{ name: 'Cash', value: summary?.cash_balance || 10000 }];

  if (loading) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400">
        <Loader2 className="animate-spin mb-4" size={48} />
        <p className="font-black uppercase text-[10px] tracking-[0.3em] text-[#0A2A4D]">Loading wealth vault...</p>
      </div>
    );
  }

  return (
    <div className="portfolio-container pb-4 space-y-8 animate-in fade-in duration-500">
      <header className="page-header flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 font-heading">Wealth Vault</h1>
          <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${user?.trading_mode === 'AUTO' ? 'bg-green-500 animate-pulse' : 'bg-orange-500'}`} />
            Agent Status: {user?.trading_mode === 'AUTO' ? 'Autonomous Optimization ACTIVE' : 'Manual Control ENABLED'}
          </p>
        </div>
        <div className="flex items-center gap-8">
          <div className="text-right">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Total Vault Value</p>
            <h2 className="text-3xl font-black text-slate-900 leading-none">
              INR {((summary?.invested_amount || 0) + (summary?.cash_balance || 0)).toLocaleString()}
            </h2>
          </div>
          <button
            onClick={() => setShowDepositModal(true)}
            className="bg-primary text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all shadow-lg shadow-primary/20"
          >
            <Plus size={18} />
            Deposit
          </button>
          <button
            onClick={() => setShowWithdrawModal(true)}
            className="bg-white text-slate-900 px-6 py-3 rounded-xl font-bold flex items-center gap-2 border border-slate-200 hover:bg-slate-50 active:scale-95 transition-all shadow-lg shadow-slate-200/40"
          >
            <ArrowDownRight size={18} />
            Withdraw
          </button>
          <Link to="/trading" className="bg-slate-900 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 transition-all shadow-lg shadow-slate-900/20">
            <Zap size={18} fill="currentColor" />
            Launch
          </Link>
        </div>
      </header>
      {fundStatus && (
        <div className={`p-3 rounded-xl border text-[10px] font-black uppercase tracking-widest ${fundStatus.type === 'success' ? 'bg-green-50 border-green-100 text-green-600' : 'bg-red-50 border-red-100 text-red-600'}`}>
          {fundStatus.msg}
        </div>
      )}

      {/* Deposit Modal */}
      {showDepositModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <Card className="w-full max-w-md bg-white p-8 rounded-3xl shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-indigo-600" />
            <button
              onClick={() => !depositing && setShowDepositModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X size={20} />
            </button>

            <div className="text-center mb-8">
              <div className="h-16 w-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4 text-primary shadow-inner">
                <DollarSign size={32} />
              </div>
              <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight">Inject Capital</h3>
              <p className="text-xs font-bold text-slate-500 mt-2 uppercase tracking-widest">Connect to Virtual Liquidity Pool</p>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Deposit Amount (INR)</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold">INR </span>
                  <input
                    type="number"
                    value={depositAmount}
                    onChange={(e) => setDepositAmount(parseInt(e.target.value))}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-8 pr-4 py-4 text-xl font-black text-slate-900 focus:ring-4 focus:ring-primary/10 transition-all outline-none"
                  />
                </div>
              </div>

              <div className="bg-slate-900 p-4 rounded-2xl text-white/80 space-y-3">
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                  <span className="opacity-60">Network Fee</span>
                  <span className="text-green-400">0.00% (PRO)</span>
                </div>
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                  <span className="opacity-60">Processing Time</span>
                  <span className="text-primary font-bold">Instant</span>
                </div>
              </div>

              <button
                onClick={handleDeposit}
                disabled={depositing}
                className="w-full py-4 bg-primary text-white rounded-2xl font-black uppercase tracking-[0.2em] shadow-xl shadow-primary/20 hover:opacity-95 transition-all flex items-center justify-center gap-3 active:scale-95"
              >
                {depositing ? <Loader2 className="animate-spin" size={18} /> : <Shield size={18} />}
                {depositing ? 'Securing Funds...' : 'Execute Deposit'}
              </button>
            </div>
          </Card>
        </div>
      )}

      {/* Withdraw Modal */}
      {showWithdrawModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <Card className="w-full max-w-md bg-white p-8 rounded-3xl shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-slate-900 to-slate-600" />
            <button
              onClick={() => !withdrawing && setShowWithdrawModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X size={20} />
            </button>

            <div className="text-center mb-8">
              <div className="h-16 w-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4 text-slate-900 shadow-inner">
                <ArrowDownRight size={32} />
              </div>
              <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight">Withdraw Capital</h3>
              <p className="text-xs font-bold text-slate-500 mt-2 uppercase tracking-widest">Cash-out from Virtual Vault</p>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Withdraw Amount (INR)</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold">INR</span>
                  <input
                    type="number"
                    value={withdrawAmount}
                    onChange={(e) => setWithdrawAmount(parseInt(e.target.value))}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-12 pr-4 py-4 text-xl font-black text-slate-900 focus:ring-4 focus:ring-slate-200 transition-all outline-none"
                  />
                </div>
              </div>

              <div className="bg-slate-900 p-4 rounded-2xl text-white/80 space-y-3">
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                  <span className="opacity-60">Processing Time</span>
                  <span className="text-primary font-bold">Instant</span>
                </div>
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                  <span className="opacity-60">Compliance Check</span>
                  <span className="text-green-400">PASS</span>
                </div>
              </div>

              <button
                onClick={handleWithdraw}
                disabled={withdrawing}
                className="w-full py-4 bg-slate-900 text-white rounded-2xl font-black uppercase tracking-[0.2em] shadow-xl shadow-slate-900/20 hover:opacity-95 transition-all flex items-center justify-center gap-3 active:scale-95"
              >
                {withdrawing ? <Loader2 className="animate-spin" size={18} /> : <Shield size={18} />}
                {withdrawing ? 'Securing Withdrawal...' : 'Execute Withdraw'}
              </button>
            </div>
          </Card>
        </div>
      )}

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
                <Target size={16} /> Active Allocation
              </h3>
              <p className="text-[10px] text-slate-500 font-bold mt-1">
                {isManual ? "Drag stocks here to allocate capital." : "Managed by Steward AI"}
              </p>
            </div>
            {!isManual && <Shield className="text-slate-400" size={20} />}
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
                      <p className="text-[10px] text-slate-500 font-mono">INR {(stock.current_price ?? stock.currentPrice ?? 0).toFixed(2)}</p>
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
          <h3 className="font-black text-slate-900 uppercase tracking-widest text-sm mb-6 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Activity size={16} /> Market Opportunities
            </div>
            <div className="flex items-center gap-1">
              <span className="h-1 w-1 bg-green-500 rounded-full animate-ping" />
              <span className="text-[8px] font-black text-slate-400">LIVE FEED</span>
            </div>
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
                  <p className="text-[10px] text-slate-400 font-mono">INR {(stock.current_price ?? stock.currentPrice ?? 0).toFixed(2)}</p>
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-8 p-4 bg-indigo-50 rounded-xl border border-indigo-100 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <h4 className="text-indigo-900 font-black text-xs uppercase tracking-widest mb-2 flex items-center justify-between">
              <span>Steward Insight</span>
              <span className="flex items-center gap-1">
                <span className="h-1 w-1 bg-indigo-400 rounded-full animate-ping" />
                <span className="text-[8px] opacity-60">LIVE</span>
              </span>
            </h4>
            <p className="text-[11px] text-indigo-700 leading-relaxed font-medium italic">
              "{appStewardPrediction?.prediction || "Market intelligence syncing..."}"
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
              <AreaChart data={history.length > 0 ? history : projections}>
                <defs>
                  <linearGradient id="colorCons" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey={history.length > 0 ? "name" : "year"} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} />
                <Tooltip
                  contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)', padding: '12px' }}
                />
                <Area type="monotone" dataKey={history.length > 0 ? "value" : "aggressive"} stroke="#10b981" strokeWidth={4} fillOpacity={1} fill="url(#colorCons)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Allocation Pie Chart */}
        <Card className="lg:col-span-4 p-8 border-slate-100 shadow-sm flex flex-col justify-center">
          <h2 className="font-black text-slate-900 uppercase text-xs tracking-widest mb-4">Portfolio Allocation</h2>
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
              <Shield size={24} />
            </div>
            <div>
              <h4 className="text-white font-black text-xs uppercase tracking-widest">SOC2 Type II</h4>
              <p className="text-[10px] opacity-70">Audited Compliance</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/5 rounded-lg text-blue-400">
              <Shield size={24} />
            </div>
            <div>
              <h4 className="text-white font-black text-xs uppercase tracking-widest">AES-256</h4>
              <p className="text-[10px] opacity-70">Bank-Grade Encryption</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/5 rounded-lg text-amber-400">
              <PieChartIcon size={24} />
            </div>
            <div>
              <h4 className="text-white font-black text-xs uppercase tracking-widest">Redundant Data</h4>
              <p className="text-[10px] opacity-70">Multi-Region Backup</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/5 rounded-lg text-purple-400">
              <TrendingUp size={24} />
            </div>
            <div>
              <h4 className="text-white font-black text-xs uppercase tracking-widest">SEBI Regulated</h4>
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

