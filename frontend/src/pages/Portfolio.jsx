import React, { useState, useEffect } from 'react';
import {
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  PieChart as PieChartIcon,
  Target,
  Shield,
  Zap,
  RefreshCcw,
  Loader2,
  Plus,
  X,
  ArrowDownRight as ArrowDownRightIcon,
  GripVertical
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { Card } from "../components/ui/card";
import { useNavigate, Link } from "react-router-dom";
import {
  fetchPortfolioSummary,
  fetchTrades,
  fetchPortfolioHistory,
  fetchExchangeStatus,
  fetchUsers,
  fetchAllPortfolios,
  depositFunds,
  fetchMarketMovers,
  fetchHoldings,
  fetchWatchlist,
  executeTrade,
  withdrawFunds
} from "../services/api";
import { useUser } from '../context/UserContext';
import { useAppData } from '../context/AppDataContext';
import { ConfidenceInvestmentCard } from '../components/ConfidenceInvestmentCard';
import { investmentService } from '../services/investmentService';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function Portfolio() {
  const { user, selectedUser } = useUser();
  const {
    summary,
    holdings: activeHoldings,
    watchlist: appWatchlist,
    projections,
    stewardPrediction: appStewardPrediction,
    marketMovers,
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
  const [activeHoldingsState, setActiveHoldingsState] = useState([]);
  const [showTopupModal, setShowTopupModal] = useState(false);
  const [topupAmount, setTopupAmount] = useState(0);
  const [basket, setBasket] = useState([]);
  const [timeRange, setTimeRange] = useState('1M');
  const [executing, setExecuting] = useState(false);
  const [basketTotal, setBasketTotal] = useState(0);
  const [showBasketModal, setShowBasketModal] = useState(false);
  const [orderTicker, setOrderTicker] = useState('');
  const [orderQty, setOrderQty] = useState(1);
  const [orderPrice, setOrderPrice] = useState(0);
  const [orderSide, setOrderSide] = useState('BUY');
  const [tradeStatus, setTradeStatus] = useState(null);
  const [strategyStatus, setStrategyStatus] = useState('IDLE');
  const [investmentReadiness, setInvestmentReadiness] = useState({
    hasCash: false,
    hasHoldings: false,
    hasActiveStrategies: false,
    isReadyForInvestment: false,
    cashBalance: 0
  });

  const navigate = useNavigate();

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load portfolio summary
        const summaryData = await fetchPortfolioSummary(selectedUser?.id || user?.id);

        // Load holdings
        const holdingsData = await fetchHoldings(selectedUser?.id || user?.id);
        setActiveHoldingsState(holdingsData || []);

        // Load watchlist
        const watchlistData = await fetchWatchlist(selectedUser?.id || user?.id);
        setWatchlist(watchlistData || []);

        // Load portfolio history
        const historyData = await fetchPortfolioHistory(selectedUser?.id || user?.id);
        setHistory(historyData || []);

        // Load investment readiness
        const userId = selectedUser?.id || user?.id;
        if (userId) {
          try {
            const readiness = await investmentService.getInvestmentReadiness(userId);
            setInvestmentReadiness(readiness);

            // Set strategy status based on active strategies
            if (readiness.hasActiveStrategies) {
              setStrategyStatus('RUNNING');
            } else {
              setStrategyStatus('IDLE');
            }
          } catch (error) {
            console.error('Error loading investment readiness:', error);
          }
        }
      } catch (error) {
        console.error('Error loading portfolio data:', error);
        // Set default data if fetch fails
        setActiveHoldingsState([]);
        setWatchlist([]);
        setHistory([]);
      }
    };

    loadData();
  }, [selectedUser, user]);

  // Handle deposit funds
  const handleDeposit = async () => {
    if (!selectedUser?.id && !user?.id) {
      setFundStatus({ type: 'error', message: 'No user selected' });
      return;
    }

    const userId = selectedUser?.id || user?.id;
    setDepositing(true);

    try {
      const result = await depositFunds(userId, depositAmount);

      if (result) {
        setFundStatus({ type: 'success', message: `Successfully deposited INR ${depositAmount}` });
        setTimeout(() => {
          setShowDepositModal(false);
          setFundStatus(null);
          // Refresh data to show updated balance
          refreshAllData();
        }, 1500);
      } else {
        setFundStatus({ type: 'error', message: 'Deposit failed' });
      }
    } catch (error) {
      console.error('Deposit error:', error);
      setFundStatus({ type: 'error', message: error.message || 'Deposit failed' });
    } finally {
      setDepositing(false);
    }
  };

  // Handle strategy launch
  const handleLaunchStrategy = async () => {
    const userId = selectedUser?.id || user?.id;
    if (!userId) {
      setTradeStatus({ type: 'error', message: 'No user selected' });
      return;
    }

    setExecuting(true);

    try {
      await investmentService.launchStrategy(userId, {
        name: "Auto Steward Primary",
        symbol: "",
        status: "RUNNING",
        execution_mode: "PAPER_TRADING"
      });

      setStrategyStatus('RUNNING');
      setInvestmentReadiness(prev => ({
        ...prev,
        isReadyForInvestment: false,
        hasActiveStrategies: true
      }));

      setTradeStatus({
        type: 'success',
        message: 'Investment strategy launched successfully! Your funds are now being actively managed.'
      });

      // Refresh data to show new holdings
      setTimeout(() => {
        refreshAllData();
      }, 2000);
    } catch (error) {
      console.error('Error launching strategy:', error);
      setTradeStatus({
        type: 'error',
        message: 'Failed to launch strategy: ' + error.message
      });
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400">
        <Loader2 className="animate-spin mb-4" size={48} />
        <p className="font-black uppercase text-[10px] tracking-[0.3em] text-slate-500">Loading wealth vault...</p>
      </div>
    );
  }

  // Calculate allocation data for pie chart
  const allocationData = activeHoldingsState.length > 0
    ? activeHoldingsState.map(h => ({
      name: h.symbol,
      value: (h.quantity || 0) * (h.current_price || h.currentPrice || h.price || 0)
    }))
    : [{ name: 'Cash', value: summary?.cash_balance || 10000 }];

  return (
    <div className="pb-4 space-y-8 animate-in fade-in duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900 font-heading">Wealth Vault</h1>
          <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${user?.trading_mode === 'AUTO' ? 'bg-green-50 animate-pulse' : 'bg-orange-500'}`} />
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
            <ArrowDownRightIcon size={18} />
            Withdraw
          </button>
          <Link to="/trading" className="bg-slate-900 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 transition-all shadow-lg shadow-slate-900/20">
            <Zap size={18} fill="currentColor" />
            Launch
          </Link>
        </div>
      </header>

      {/* Deposit Modal */}
      {showDepositModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md border border-slate-100 shadow-2xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-black text-slate-900">Deposit Funds</h3>
              <button
                onClick={() => {
                  setShowDepositModal(false);
                  setFundStatus(null);
                }}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Amount (INR)</label>
                <input
                  type="number"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(Number(e.target.value))}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                  placeholder="Enter amount"
                  min="1"
                />
              </div>

              {fundStatus && (
                <div className={`p-3 rounded-xl border text-[10px] font-black uppercase tracking-widest ${fundStatus.type === 'success'
                  ? 'bg-green-50 border-green-100 text-green-600'
                  : 'bg-red-50 border-red-100 text-red-600'
                  }`}>
                  {fundStatus.message}
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => {
                    setShowDepositModal(false);
                    setFundStatus(null);
                  }}
                  disabled={depositing}
                  className="flex-1 bg-slate-100 text-slate-700 px-4 py-3 rounded-xl font-black text-sm hover:bg-slate-200 transition-all disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeposit}
                  disabled={depositing || depositAmount <= 0}
                  className="flex-1 bg-primary text-white px-4 py-3 rounded-xl font-black text-sm hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {depositing ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                  {depositing ? 'Processing...' : 'Deposit'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Withdraw Modal */}
      {showWithdrawModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md border border-slate-100 shadow-2xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-black text-slate-900">Withdraw Funds</h3>
              <button
                onClick={() => {
                  setShowWithdrawModal(false);
                  setFundStatus(null);
                }}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Amount (INR)</label>
                <input
                  type="number"
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(Number(e.target.value))}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                  placeholder="Enter amount"
                  min="1"
                />
              </div>

              {fundStatus && (
                <div className={`p-3 rounded-xl border text-[10px] font-black uppercase tracking-widest ${fundStatus.type === 'success'
                  ? 'bg-green-50 border-green-100 text-green-600'
                  : 'bg-red-50 border-red-100 text-red-600'
                  }`}>
                  {fundStatus.message}
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => {
                    setShowWithdrawModal(false);
                    setFundStatus(null);
                  }}
                  disabled={withdrawing}
                  className="flex-1 bg-slate-100 text-slate-700 px-4 py-3 rounded-xl font-black text-sm hover:bg-slate-200 transition-all disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    if (!selectedUser?.id && !user?.id) {
                      setFundStatus({ type: 'error', message: 'No user selected' });
                      return;
                    }

                    const userId = selectedUser?.id || user?.id;

                    // Validation: Check if withdrawal amount exceeds cash balance
                    if (withdrawAmount > (summary?.cash_balance || 0)) {
                      setFundStatus({ type: 'error', message: 'Insufficient cash balance' });
                      return;
                    }

                    setWithdrawing(true);

                    try {
                      const result = await withdrawFunds(userId, withdrawAmount);

                      if (result) {
                        setFundStatus({ type: 'success', message: `Successfully withdrew INR ${withdrawAmount}` });
                        setTimeout(() => {
                          setShowWithdrawModal(false);
                          setFundStatus(null);
                          // Refresh data to show updated balance
                          refreshAllData();
                        }, 1500);
                      } else {
                        setFundStatus({ type: 'error', message: 'Withdrawal failed' });
                      }
                    } catch (error) {
                      console.error('Withdrawal error:', error);
                      setFundStatus({ type: 'error', message: error.message || 'Withdrawal failed' });
                    } finally {
                      setWithdrawing(false);
                    }
                  }}
                  disabled={withdrawing || withdrawAmount <= 0}
                  className="flex-1 bg-red-600 text-white px-4 py-3 rounded-xl font-black text-sm hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {withdrawing ? <Loader2 size={16} className="animate-spin" /> : <ArrowDownRightIcon size={16} />}
                  {withdrawing ? 'Processing...' : 'Withdraw'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Confidence Investment Card - Show when cash exists but no holdings */}
      {investmentReadiness.isReadyForInvestment && (
        <ConfidenceInvestmentCard
          cashBalance={summary?.cash_balance || 0}
          investedAmount={summary?.invested_amount || 0}
          onLaunchStrategy={handleLaunchStrategy}
          isLoading={executing}
          strategyStatus={strategyStatus}
          userRole={user?.role || 'TRADER'}
        />
      )}

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Net Worth</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">INR {summary?.total_value?.toLocaleString() || '0'}</h3>
            </div>
            <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
              <DollarSign className="text-primary" size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Cash Balance</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">INR {summary?.cash_balance?.toLocaleString() || '0'}</h3>
            </div>
            <div className="h-12 w-12 rounded-xl bg-green-100 flex items-center justify-center">
              <TrendingUp className="text-green-600" size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Invested Amount</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">INR {summary?.invested_amount?.toLocaleString() || '0'}</h3>
            </div>
            <div className="h-12 w-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <Activity className="text-blue-600" size={24} />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-black text-slate-400 uppercase tracking-widest">Today's PnL</p>
              <h3 className={`text-2xl font-black mt-1 ${summary?.today_pnl >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                {summary?.today_pnl >= 0 ? '+' : ''}INR {summary?.today_pnl?.toLocaleString() || '0'}
              </h3>
            </div>
            <div className={`h-12 w-12 rounded-xl ${summary?.today_pnl >= 0 ? 'bg-green-100' : 'bg-red-100'} flex items-center justify-center`}>
              {summary?.today_pnl >= 0 ? (
                <TrendingUp className="text-green-600" size={24} />
              ) : (
                <TrendingDown className="text-red-500" size={24} />
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* Portfolio Value Chart */}
      <Card className="p-6 border-slate-100 shadow-sm bg-white">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-black text-slate-900">Portfolio Value Over Time</h3>
          <div className="flex gap-2">
            {['1M', '3M', '6M', '1Y'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1.5 text-xs font-black rounded-lg transition-all ${timeRange === range ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history.slice(-(timeRange === '1M' ? 30 : timeRange === '3M' ? 90 : timeRange === '6M' ? 180 : 365))}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickFormatter={(value) => `₹${value.toLocaleString()}`}
              />
              <Tooltip
                formatter={(value) => [`₹${value.toLocaleString()}`, 'Value']}
                contentStyle={{
                  borderRadius: '12px',
                  border: 'none',
                  boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorValue)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Holdings and Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <h3 className="text-lg font-black text-slate-900 mb-6">Current Holdings</h3>

          <div className="space-y-4">
            {activeHoldingsState.length > 0 ? (
              activeHoldingsState.map((holding, index) => {
                const currentValue = (holding.quantity || 0) * (holding.current_price || holding.currentPrice || holding.price || 0);
                const investedValue = (holding.quantity || 0) * (holding.avg_price || holding.avgPrice || holding.avg_cost || 0);
                const pnl = currentValue - investedValue;
                const pnlPercent = investedValue > 0 ? (pnl / investedValue) * 100 : 0;

                return (
                  <div key={index} className="flex items-center justify-between p-4 border border-slate-100 rounded-xl hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-xl bg-slate-100 flex items-center justify-center font-black text-slate-700">
                        {holding.symbol?.substring(0, 2)}
                      </div>
                      <div>
                        <h4 className="font-black text-slate-900">{holding.symbol}</h4>
                        <p className="text-sm text-slate-500">{holding.quantity || 0} shares</p>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="font-black text-slate-900">INR {(holding.current_price || holding.currentPrice || holding.price || 0).toFixed(2)}</p>
                      <p className={`text-sm font-black ${pnlPercent >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                        {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
                      </p>
                      <p className={`text-xs ${pnl >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                        {pnl >= 0 ? '+' : ''}INR {pnl.toFixed(2)}
                      </p>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12 text-slate-400">
                <Activity size={48} className="mx-auto mb-4 opacity-50" />
                <h4 className="font-black text-slate-500 mb-2">No Holdings</h4>
                <p className="text-sm">Your investment positions will appear here</p>
              </div>
            )}
          </div>
        </Card>

        <Card className="p-6 border-slate-100 shadow-sm bg-white">
          <h3 className="text-lg font-black text-slate-900 mb-6">Asset Allocation</h3>

          <div className="h-80 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  nameKey="name"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`INR ${value.toLocaleString()}`, 'Value']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* New Strategy Launch Section */}
      <Card className="p-8 border-slate-200 shadow-xl bg-slate-900 text-white overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/20 rounded-full blur-3xl -mr-32 -mt-32" />
        <div className="relative z-10">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h3 className="text-2xl font-black uppercase tracking-tight">Available Mandates</h3>
              <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mt-1">Select an autonomous strategy to deploy</p>
            </div>
            <Zap size={32} className="text-primary animate-pulse" fill="currentColor" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { id: 'equity-long', name: 'Alpha Quant Long', type: 'EQUITY', risk: 'LOW', return: '18% p.a.', desc: 'High-conviction equity accumulation based on volume anomalies.' },
              { id: 'options-income', name: 'Delta Neutral Seller', type: 'OPTIONS', risk: 'MEDIUM', return: '24% p.a.', desc: 'Weekly option selling strategy targeting theta decay.' },
              { id: 'momentum-pro', name: 'Momentum Scalper', type: 'MULTI-ASSET', risk: 'HIGH', return: '35% p.a.', desc: 'Aggressive trend-following across indices and large caps.' },
            ].map((strat) => (
              <div key={strat.id} className="bg-white/5 border border-white/10 p-5 rounded-2xl hover:bg-white/10 transition-all group">
                <div className="flex justify-between items-start mb-4">
                  <div className={`px-3 py-1 rounded-full text-[8px] font-black uppercase tracking-widest ${strat.risk === 'LOW' ? 'bg-green-500/20 text-green-400' : strat.risk === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' : 'bg-red-500/20 text-red-400'}`}>
                    {strat.risk} RISK
                  </div>
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{strat.type}</span>
                </div>
                <h4 className="text-lg font-black mb-1">{strat.name}</h4>
                <p className="text-xs text-slate-400 line-clamp-2 h-8 mb-4">{strat.desc}</p>
                <div className="flex justify-between items-center bg-white/5 p-3 rounded-xl mb-4">
                  <div>
                    <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Est. Return</p>
                    <p className="text-sm font-black text-green-400">{strat.return}</p>
                  </div>
                  <Shield size={16} className="text-primary/60" />
                </div>
                <button
                  onClick={() => handleLaunchStrategy()}
                  disabled={executing}
                  className="w-full py-3 bg-primary text-white rounded-xl font-black text-xs uppercase tracking-[0.2em] shadow-lg shadow-primary/20 hover:opacity-95 transition-all active:scale-95 flex items-center justify-center gap-2 group-hover:bg-primary-dark"
                >
                  {executing ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} fill="currentColor" />}
                  Deploy Mandate
                </button>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Transaction Records Loader Overlay */}
      {executing && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm">
          <div className="bg-white p-8 rounded-3xl shadow-2xl flex flex-col items-center">
            <Loader2 size={48} className="text-primary animate-spin mb-4" />
            <p className="font-black text-slate-900 uppercase tracking-[0.2em] text-xs">Synchronizing with Node...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Portfolio;