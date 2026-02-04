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
  executeTrade
} from "../services/api";
import { useUser } from '../context/UserContext';
import { useAppData } from '../context/AppDataContext';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function Portfolio() {
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
  const [activeHoldingsState, setActiveHoldingsState] = useState([]);
  const [showTopupModal, setShowTopupModal] = useState(false);
  const [topupAmount, setTopupAmount] = useState(0);
  const [basket, setBasket] = useState([]);
  const [executing, setExecuting] = useState(false);
  const [basketTotal, setBasketTotal] = useState(0);
  const [showBasketModal, setShowBasketModal] = useState(false);
  const [orderTicker, setOrderTicker] = useState('');
  const [orderQty, setOrderQty] = useState(1);
  const [orderPrice, setOrderPrice] = useState(0);
  const [orderSide, setOrderSide] = useState('BUY');
  const [tradeStatus, setTradeStatus] = useState(null);

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

  // Handle manual trade
  const handleManualTrade = async (side) => {
    if (!orderTicker || orderQty <= 0) {
      setTradeStatus({ type: 'error', message: 'Please select a ticker and quantity' });
      return;
    }

    setExecuting(true);
    try {
      const tradeData = {
        symbol: orderTicker,
        side: side,
        quantity: orderQty,
        price: orderPrice || null,
        order_type: 'MARKET',
        user_id: user.id
      };

      const result = await executeTrade(user.id, tradeData);
      
      if (result.success) {
        setTradeStatus({ 
          type: 'success', 
          message: `${side} order placed successfully for ${orderQty} shares of ${orderTicker}` 
        });
        
        // Refresh data
        await refreshAllData();
        
        // Clear form
        setOrderQty(1);
        setOrderPrice(0);
      } else {
        setTradeStatus({ 
          type: 'error', 
          message: result.error || 'Trade execution failed' 
        });
      }
    } catch (error) {
      setTradeStatus({ 
        type: 'error', 
        message: error.message || 'An error occurred during trade execution' 
      });
    } finally {
      setExecuting(false);
    }
  };

  // Add to basket
  const addToBasket = () => {
    if (!orderTicker || orderQty <= 0) {
      setTradeStatus({ type: 'error', message: 'Invalid order details' });
      return;
    }

    const newOrder = {
      id: Date.now(),
      symbol: orderTicker,
      side: orderSide,
      quantity: orderQty,
      price: orderPrice,
      type: 'MARKET'
    };

    setBasket(prev => [...prev, newOrder]);
    setTradeStatus({ type: 'success', message: `Added ${orderQty} ${orderTicker} to basket` });
  };

  // Execute basket
  const executeBasket = async () => {
    if (basket.length === 0) return;

    setExecuting(true);
    try {
      for (const order of basket) {
        await executeTrade(user.id, {
          symbol: order.symbol,
          side: order.side,
          quantity: order.quantity,
          price: order.price,
          order_type: order.type,
        });
      }
      
      setTradeStatus({ 
        type: 'success', 
        message: `Executed ${basket.length} orders from basket` 
      });
      
      setBasket([]);
      setShowBasketModal(false);
      await refreshAllData();
    } catch (error) {
      setTradeStatus({ 
        type: 'error', 
        message: 'Basket execution failed: ' + error.message 
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
            <ArrowDownRightIcon size={18} />
            Withdraw
          </button>
          <Link to="/trading" className="bg-slate-900 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 transition-all shadow-lg shadow-slate-900/20">
            <Zap size={18} fill="currentColor" />
            Launch
          </Link>
        </div>
      </header>

      {tradeStatus && (
        <div className={`p-3 rounded-xl border text-[10px] font-black uppercase tracking-widest ${
          tradeStatus.type === 'success' 
            ? 'bg-green-50 border-green-100 text-green-600' 
            : 'bg-red-50 border-red-100 text-red-600'
        }`}>
          {tradeStatus.message}
        </div>
      )}

      {/* Manual Trading Panel */}
      <Card className="p-6 border-slate-100 shadow-sm bg-white">
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="flex-1">
            <h3 className="text-lg font-black text-slate-900 mb-4">Manual Order Ticket</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Symbol</label>
                <input
                  type="text"
                  value={orderTicker}
                  onChange={(e) => setOrderTicker(e.target.value.toUpperCase())}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                  placeholder="Enter symbol (e.g., RELIANCE)"
                />
              </div>
              
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Quantity</label>
                <input
                  type="number"
                  value={orderQty}
                  onChange={(e) => setOrderQty(parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                  placeholder="Enter quantity"
                />
              </div>
              
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Side</label>
                <select
                  value={orderSide}
                  onChange={(e) => setOrderSide(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                >
                  <option value="BUY">Buy</option>
                  <option value="SELL">Sell</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-black text-slate-700 mb-2">Price</label>
                <input
                  type="number"
                  value={orderPrice}
                  onChange={(e) => setOrderPrice(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                  placeholder="Enter price (leave blank for market)"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => handleManualTrade('BUY')}
                disabled={executing}
                className="flex-1 bg-green-600 text-white px-6 py-3.5 rounded-xl font-black text-sm uppercase tracking-widest hover:bg-green-700 transition-all shadow-lg shadow-green-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {executing ? <RefreshCcw className="animate-spin" size={18} /> : <TrendingUp size={18} />}
                Buy
              </button>
              
              <button
                onClick={() => handleManualTrade('SELL')}
                disabled={executing}
                className="flex-1 bg-red-600 text-white px-6 py-3.5 rounded-xl font-black text-sm uppercase tracking-widest hover:bg-red-700 transition-all shadow-lg shadow-red-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {executing ? <RefreshCcw className="animate-spin" size={18} /> : <TrendingDown size={18} />}
                Sell
              </button>
              
              <button
                onClick={addToBasket}
                className="px-6 py-3.5 rounded-xl font-black text-sm uppercase tracking-widest bg-slate-900 text-white hover:bg-slate-800 transition-all"
              >
                Add to Basket
              </button>
            </div>
          </div>
          
          <div className="lg:w-80">
            <h3 className="text-lg font-black text-slate-900 mb-4">Quick Actions</h3>
            
            <div className="space-y-3">
              <button
                onClick={() => setShowBasketModal(true)}
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-black text-slate-900">Order Basket</span>
                  <span className="text-xs font-black bg-primary text-white px-2 py-1 rounded-full">
                    {basket.length}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">Batch execute multiple orders</p>
              </button>
              
              <button
                onClick={() => setShowTopupModal(true)}
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <DollarSign size={16} className="text-primary" />
                  <span className="font-black text-slate-900">Quick Top-up</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">Add funds instantly</p>
              </button>
              
              <button className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors">
                <div className="flex items-center gap-2">
                  <Activity size={16} className="text-primary" />
                  <span className="font-black text-slate-900">Risk Analyzer</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">Portfolio risk assessment</p>
              </button>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Active Holdings */}
        <Card className="lg:col-span-8 p-6 border-slate-100 shadow-sm bg-white">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-black text-slate-900">Active Holdings</h3>
            <span className="text-sm font-black bg-primary/10 text-primary px-3 py-1 rounded-full">
              {activeHoldingsState.length} positions
            </span>
          </div>
          
          <div className="space-y-4">
            {activeHoldingsState.length > 0 ? (
              activeHoldingsState.map((holding, i) => {
                const currentPrice = holding.current_price || holding.currentPrice || holding.price || 0;
                const avgPrice = holding.avg_price || holding.avgPrice || 0;
                const pnl = (currentPrice - avgPrice) * (holding.quantity || 0);
                const pnlPercent = avgPrice > 0 ? ((currentPrice - avgPrice) / avgPrice) * 100 : 0;
                
                return (
                  <div key={i} className="p-4 border border-slate-100 rounded-xl bg-slate-50 hover:bg-white transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="h-12 w-12 rounded-xl bg-slate-100 flex items-center justify-center font-black text-slate-700">
                          {holding.symbol?.substring(0, 2)}
                        </div>
                        <div>
                          <h4 className="font-black text-slate-900">{holding.symbol}</h4>
                          <p className="text-xs text-slate-500">{holding.quantity || 0} shares @ INR {(avgPrice || 0).toFixed(2)}</p>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <p className="font-black text-slate-900">INR {currentPrice.toFixed(2)}</p>
                        <p className={`text-sm font-black ${pnlPercent >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                          {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
                        </p>
                        <p className={`text-xs font-bold ${pnl >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                          {pnl >= 0 ? '+' : ''}INR {pnl.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12 text-slate-400">
                <Activity size={48} className="mx-auto mb-4 opacity-50" />
                <h4 className="font-black text-slate-500 mb-2">No Active Holdings</h4>
                <p className="text-sm">Place your first trade to see active positions here</p>
              </div>
            )}
          </div>
        </Card>

        {/* Portfolio Allocation */}
        <Card className="lg:col-span-4 p-6 border-slate-100 shadow-sm bg-white">
          <h3 className="text-lg font-black text-slate-900 mb-6">Portfolio Allocation</h3>
          
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
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
          
          <div className="mt-6 space-y-2">
            {allocationData.map((item, index) => (
              <div key={index} className="flex justify-between text-sm">
                <span className="font-bold text-slate-700">{item.name}</span>
                <span className="font-black text-slate-900">INR {item.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Wealth Projection Chart */}
      <Card className="p-8 border-slate-100 shadow-sm bg-white">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="font-black text-slate-900 uppercase text-xs tracking-widest">Wealth Projection</h2>
            <p className="text-xs text-slate-400 font-medium mt-1">Estimated growth based on current allocation</p>
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
            <AreaChart data={history.length > 0 ? history : [
              { name: 'Jan', value: 100000 },
              { name: 'Feb', value: 102000 },
              { name: 'Mar', value: 98000 },
              { name: 'Apr', value: 105000 },
              { name: 'May', value: 107000 },
              { name: 'Jun', value: 110000 }
            ]}>
              <defs>
                <linearGradient id="colorCons" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis 
                dataKey="name" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} 
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} 
                tickFormatter={(val) => `INR ${val}`}
              />
              <Tooltip 
                formatter={(value) => [`INR ${value}`, 'Value']}
                contentStyle={{ 
                  borderRadius: '16px', 
                  border: 'none', 
                  boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)', 
                  padding: '12px' 
                }}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#10b981" 
                strokeWidth={4} 
                fillOpacity={1} 
                fill="url(#colorCons)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Watchlist */}
      <Card className="p-6 border-slate-100 shadow-sm bg-white">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-black text-slate-900">Watchlist</h3>
          <span className="text-sm font-black bg-slate-100 text-slate-600 px-3 py-1 rounded-full">
            {watchlist.length} stocks
          </span>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {watchlist.length > 0 ? (
            watchlist.map((stock, i) => {
              const currentPrice = stock.current_price || stock.currentPrice || stock.price || 0;
              const change = stock.change || stock.change_pct || 0;
              
              return (
                <Link to="/trading" key={i} className="block">
                  <div className="p-4 border border-slate-100 rounded-xl bg-slate-50 hover:bg-white hover:border-primary/30 hover:shadow-md transition-all cursor-pointer">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-black text-slate-900 text-sm">{stock.symbol}</h4>
                      <span className={`text-xs font-black px-2 py-0.5 rounded-full ${
                        (typeof change === 'string' ? parseFloat(change) : change) >= 0 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-red-100 text-red-500'
                      }`}>
                        {(typeof change === 'string' ? parseFloat(change) : change) >= 0 ? '+' : ''}
                        {(typeof change === 'string' ? parseFloat(change) : change).toFixed(2)}%
                      </span>
                    </div>
                    <p className="text-sm font-black text-slate-900">INR {currentPrice.toFixed(2)}</p>
                  </div>
                </Link>
              );
            })
          ) : (
            <div className="col-span-full text-center py-12 text-slate-400">
              <Activity size={48} className="mx-auto mb-4 opacity-50" />
              <h4 className="font-black text-slate-500 mb-2">Empty Watchlist</h4>
              <p className="text-sm">Add stocks to your watchlist to track them here</p>
            </div>
          )}
        </div>
      </Card>

      {/* AI Steward Prediction */}
      <Card className="p-6 border-slate-100 shadow-sm bg-gradient-to-br from-indigo-50 to-slate-50">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center">
            <Zap size={20} className="text-white" />
          </div>
          <div>
            <h3 className="font-black text-slate-900">AI Steward Prediction</h3>
            <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Intelligent Market Analysis</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-xl border border-indigo-100">
          <p className="text-slate-700 italic leading-relaxed">
            "{appStewardPrediction?.prediction || "AI is analyzing market conditions and generating insights..."}"
          </p>
          
          <div className="flex flex-wrap gap-6 mt-6 pt-6 border-t border-slate-100">
            <div>
              <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Recommendation</p>
              <p className={`font-black text-lg ${appStewardPrediction?.decision === 'BUY' ? 'text-green-600' : appStewardPrediction?.decision === 'SELL' ? 'text-red-500' : 'text-slate-600'}`}>
                {appStewardPrediction?.decision || 'HOLD'}
              </p>
            </div>
            
            <div>
              <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Confidence</p>
              <p className="font-black text-lg text-slate-900">
                {appStewardPrediction?.confidence || 0}%
              </p>
            </div>
            
            <div>
              <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Risk Level</p>
              <p className="font-black text-lg text-slate-900">
                {appStewardPrediction?.risk_level || 'MODERATE'}
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}

