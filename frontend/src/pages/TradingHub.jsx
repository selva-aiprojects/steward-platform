import React, { useState, useEffect, useMemo } from 'react';
import { Card } from "../components/ui/card";
import { 
  Play, 
  Pause, 
  RefreshCcw, 
  Zap, 
  Target, 
  TrendingUp, 
  TrendingDown, 
  ArrowUpRight, 
  Shield, 
  Loader2, 
  Lock, 
  Unlock, 
  Settings2, 
  X, 
  ArrowRight, 
  Activity,
  ShoppingBag,
  Unlock as UnlockIcon,
  Lock as LockIcon
} from 'lucide-react';
import { 
  fetchStrategies, 
  fetchProjections, 
  fetchUser, 
  updateUser, 
  fetchPortfolioHistory, 
  fetchPortfolioSummary, 
  fetchExchangeStatus, 
  executeTrade, 
  fetchHoldings, 
  launchStrategy, 
  depositFunds 
} from "../services/api";

import { useUser } from "../context/UserContext";
import { useAppData } from "../context/AppDataContext";

export function TradingHub() {
    const { user: contextUser } = useUser();
    const {
        summary,
        projections,
        strategies: appStrategies,
        exchangeStatus,
        stewardPrediction: appStewardPrediction,
        marketResearch,
        marketMovers,
        watchlist,
        loading,
        refreshAllData,
        toggleTradingMode: toggleUserTradingMode
    } = useAppData();

    const [strategies, setStrategies] = useState([]);
    const [toggling, setToggling] = useState(false);
    const [executing, setExecuting] = useState(false);
    const [provisioning, setProvisioning] = useState(false);
    const [showLaunchModal, setShowLaunchModal] = useState(false);
    const [newStratSymbol, setNewStratSymbol] = useState('TCS');
    const [newStratName, setNewStratName] = useState('TCS Momentum');
    const [logs, setLogs] = useState([
        { id: 1, time: new Date().toLocaleTimeString(), msg: "Initializing Global Watcher node...", type: 'system' },
        { id: 2, time: new Date().toLocaleTimeString(), msg: "Analyzing RSI divergence on Nifty 50 complex...", type: 'logic' }
    ]);
    const [orderTicker, setOrderTicker] = useState('RELIANCE');
    const [orderQty, setOrderQty] = useState(10);
    const [basket, setBasket] = useState([]);
    const [showBasketModal, setShowBasketModal] = useState(false);
    const [showTopupModal, setShowTopupModal] = useState(false);
    const [topupAmount, setTopupAmount] = useState(0);
    const [activeHoldings, setActiveHoldings] = useState([]);
    const [tradeStatus, setTradeStatus] = useState(null);
    const [executingBasket, setExecutingBasket] = useState(false);
    const user = contextUser;

    useEffect(() => {
        const interval = setInterval(() => {
            const types = ['logic', 'system', 'trade'];
            const msgs = [
                "Evaluating order book depth on HDFCBANK...",
                "Sentiment analysis shift detected on social nodes.",
                "Adjusting stop-loss threshold for active mandates.",
                "Handshake pulse successful with NSE execution node.",
                "Optimization loop 842 completed."
            ];
            const newLog = {
                id: Date.now(),
                time: new Date().toLocaleTimeString(),
                msg: msgs[Math.floor(Math.random() * msgs.length)],
                type: types[Math.floor(Math.random() * types.length)]
            };
            setLogs(prev => [newLog, ...prev].slice(0, 10));
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (appStrategies) setStrategies(appStrategies);
    }, [appStrategies]);

    useEffect(() => {
        const loadHoldings = async () => {
            if (!contextUser) return;
            try {
                const currentHoldings = await fetchHoldings(contextUser.id);
                setActiveHoldings(Array.isArray(currentHoldings) ? currentHoldings : []);
            } catch (err) {
                console.error("Failed to load holdings:", err);
            }
        };
        loadHoldings();
    }, [contextUser]);

    const toggleTradingMode = async () => {
        setToggling(true);
        try {
            await toggleUserTradingMode();
        } finally {
            setToggling(false);
        }
    };

    const handleManualTrade = async (action) => {
        if (!user || !orderTicker || orderQty <= 0) {
            setTradeStatus({ type: 'error', msg: 'Select a valid ticker and quantity.' });
            setTimeout(() => setTradeStatus(null), 4000);
            return;
        }

        setExecuting(true);
        try {
            const normalizedSymbol = orderTicker.includes(':') ? orderTicker.split(':').pop() : orderTicker;
            const tradeData = {
                symbol: normalizedSymbol,
                side: action, // BUY or SELL
                quantity: orderQty,
                price: 2450.00, // Mock live price fallback
                order_type: 'MARKET',
                user_id: user.id,
                decision_logic: `User manual override: Explicit ${action} command executed via Trading Hub.`
            };

            const result = await executeTrade(user.id, tradeData);
            if (result?.status === 'INSUFFICIENT_FUNDS') {
                const required = result.required_cash || 0;
                setTopupAmount(Math.ceil(required));
                setShowTopupModal(true);
                setExecuting(false);
                return;
            }
            if (result) {
                await refreshAllData();
                const updatedHoldings = await fetchHoldings(user.id);
                setActiveHoldings(updatedHoldings);
                setTradeStatus({ type: 'success', msg: `${action} successful: ${orderQty} units of ${orderTicker}` });
                setTimeout(() => setTradeStatus(null), 5000);
            }
        } catch (err) {
            console.error("Manual trade failed:", err);
            setTradeStatus({ type: 'error', msg: `Trade Failed: ${err.message}` });
            setTimeout(() => setTradeStatus(null), 5000);
        } finally {
            setExecuting(false);
        }
    };

    const addToBasket = () => {
        if (!orderTicker || orderQty <= 0) {
            setTradeStatus({ type: 'error', msg: 'Select a valid ticker and quantity.' });
            setTimeout(() => setTradeStatus(null), 4000);
            return;
        }
        const normalized = orderTicker.includes(':') ? orderTicker.split(':').pop() : orderTicker;
        const price = 2450.00; // Mock price - would come from market data in real implementation
        setBasket(prev => ([...prev, {
            id: Date.now(),
            symbol: normalized,
            quantity: orderQty,
            price: price,
            side: 'BUY'
        }]));
        setTradeStatus({ type: 'success', msg: `Added ${orderQty} ${normalized} to basket.` });
        setTimeout(() => setTradeStatus(null), 3000);
    };

    const removeFromBasket = (id) => {
        setBasket(prev => prev.filter(item => item.id !== id));
    };

    const basketTotal = basket.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    const executeBasket = async () => {
        if (!user || basket.length === 0) return;

        setExecutingBasket(true);
        try {
            for (const item of basket) {
                await executeTrade(user.id, {
                    symbol: item.symbol,
                    side: item.side,
                    quantity: item.quantity,
                    price: item.price,
                    order_type: 'MARKET',
                    decision_logic: `Basket order: ${item.side} ${item.quantity} ${item.symbol}`
                });
            }
            await refreshAllData();
            const updatedHoldings = await fetchHoldings(user.id);
            setActiveHoldings(updatedHoldings);
            setBasket([]);
            setTradeStatus({ type: 'success', msg: 'Basket executed successfully.' });
            setTimeout(() => setTradeStatus(null), 4000);
            setShowBasketModal(false);
        } catch (err) {
            console.error('Basket trade failed:', err);
            setTradeStatus({ type: 'error', msg: 'Basket execution failed.' });
            setTimeout(() => setTradeStatus(null), 4000);
        } finally {
            setExecutingBasket(false);
        }
    };

    const handleLaunchStrategy = async () => {
        if (!contextUser) return;
        setProvisioning(true);
        try {
            const stratData = {
                name: newStratName,
                symbol: newStratSymbol,
                status: 'RUNNING',
                pnl: 0,
                trades: '0'
            };
            const result = await launchStrategy(contextUser.id, stratData);
            if (result) {
                setStrategies(prev => [...prev, result]);
                setShowLaunchModal(false);
                setNewStratName('');
                setNewStratSymbol('');
                alert(`Strategy ${newStratName} (${newStratSymbol}) successfully provisioned and deployed.`);
            }
        } catch (err) {
            console.error("Launch failed:", err);
        } finally {
            setProvisioning(false);
        }
    };

    if (loading) {
        return (
            <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400">
                <Loader2 className="animate-spin mb-4" size={32} />
                <p className="font-bold uppercase text-[10px] tracking-widest text-[#0A2A4D]">Synchronizing Execution Parameters...</p>
            </div>
        );
    }

    const symbolOptions = useMemo(() => {
        const base = [
            { symbol: 'RELIANCE', exchange: 'NSE' },
            { symbol: 'TCS', exchange: 'NSE' },
            { symbol: 'HDFCBANK', exchange: 'NSE' },
            { symbol: 'INFY', exchange: 'NSE' },
            { symbol: 'ICICIBANK', exchange: 'NSE' },
            { symbol: 'SENSEX', exchange: 'BSE' },
            { symbol: 'BOM500002', exchange: 'BSE' },
            { symbol: 'BOM500010', exchange: 'BSE' },
            { symbol: 'GOLD', exchange: 'MCX' },
            { symbol: 'SILVER', exchange: 'MCX' },
            { symbol: 'CRUDEOIL', exchange: 'MCX' },
            { symbol: 'NATURALGAS', exchange: 'MCX' }
        ];

        const fromHoldings = (activeHoldings || []).map(h => ({ 
          symbol: h.symbol, 
          exchange: h.exchange || 'NSE' 
        }));
        const fromWatchlist = (watchlist || []).map(w => ({ 
          symbol: w.symbol, 
          exchange: w.exchange || 'NSE' 
        }));
        const fromMovers = (marketMovers || []).map(m => ({ 
          symbol: m.symbol, 
          exchange: m.exchange || 'NSE' 
        }));
        const fromProjections = (projections || []).map(p => ({ 
          symbol: p.ticker, 
          exchange: 'NSE' 
        }));

        const combined = [...base, ...fromHoldings, ...fromWatchlist, ...fromMovers, ...fromProjections];
        const seen = new Set();
        return combined.filter(item => {
            if (!item.symbol) return false;
            const key = `${item.exchange}:${item.symbol}`;
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
        });
    }, [activeHoldings, watchlist, marketMovers, projections]);

    useEffect(() => {
        if (symbolOptions.length > 0 && !orderTicker) {
            setOrderTicker(symbolOptions[0].symbol);
        }
    }, [symbolOptions, orderTicker]);

    return (
        <div data-testid="trading-hub-container" className="pb-4 space-y-8 animate-in slide-in-from-bottom-4 duration-500">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900 font-heading">Trading Hub</h1>
                    <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none flex items-center gap-2">
                        <span data-testid="algo-status" className={`h-2 w-2 rounded-full ${user?.trading_mode === 'AUTO' ? 'bg-green-500 animate-pulse' : 'bg-orange-500'}`} />
                        Algo Engine: {user?.trading_mode === 'AUTO' ? 'Autonomous Mode Active' : 'Manual Override Active'}
                    </p>
                </div>

                <div className="flex items-center gap-3 bg-slate-50 p-1.5 rounded-2xl border border-slate-100 shadow-inner">
                    <button
                        data-testid="mode-toggle-auto"
                        onClick={() => user?.trading_mode !== 'AUTO' && toggleTradingMode()}
                        disabled={toggling}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${user?.trading_mode === 'AUTO'
                            ? 'bg-primary text-white shadow-xl shadow-primary/40 ring-4 ring-primary/10 scale-105'
                            : 'bg-white text-slate-400 hover:text-slate-600 opacity-60 border border-slate-200'
                            }`}
                    >
                        {user?.trading_mode === 'AUTO' ? <Shield size={14} className="animate-pulse" /> : <LockIcon size={14} />}
                        Steward Auto
                    </button>
                    <button
                        data-testid="mode-toggle-manual"
                        onClick={() => user?.trading_mode !== 'MANUAL' && toggleTradingMode()}
                        disabled={toggling}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 ${user?.trading_mode === 'MANUAL'
                            ? 'bg-orange-600 text-white shadow-xl shadow-orange-600/40 ring-4 ring-orange-500/10 scale-105'
                            : 'bg-white text-slate-400 hover:text-slate-600 opacity-60 border border-slate-200'
                            }`}
                    >
                        {user?.trading_mode === 'MANUAL' ? <UnlockIcon size={14} className="animate-bounce" /> : <Shield size={14} />}
                        Manual Mode
                    </button>
                </div>

                <div className="h-10 w-[1px] bg-slate-100 hidden md:block mx-4" />

                <div className="flex flex-col items-end mr-4">
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Exchange Status</span>
                    <div className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-[10px] font-black text-slate-900">{exchangeStatus?.exchange || 'NSE'} {exchangeStatus?.latency || 'ONLINE'}</span>
                    </div>
                </div>

                <button
                    onClick={() => setShowLaunchModal(true)}
                    className="bg-primary text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all shadow-lg shadow-primary/20 group"
                >
                    <Zap size={18} fill="currentColor" className="group-hover:animate-bounce" />
                    Launch New Strategy
                </button>
            </header>

            {/* Strategy Provisioning Modal */}
            {showLaunchModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
                    <div className="w-full max-w-md bg-white p-8 rounded-3xl shadow-2xl relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-green-500" />
                        <button
                            onClick={() => !provisioning && setShowLaunchModal(false)}
                            className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            <X size={20} />
                        </button>

                        <div className="text-center mb-8">
                            <div className="h-16 w-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4 text-primary shadow-inner">
                                <Zap size={32} fill="currentColor" />
                            </div>
                            <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight">Provision Agent Mandate</h3>
                            <p className="text-xs font-bold text-slate-500 mt-2 uppercase tracking-widest">Deploy New Autonomous Trading Node</p>
                        </div>

                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Strategy Name</label>
                                <input
                                    type="text"
                                    value={newStratName}
                                    onChange={(e) => setNewStratName(e.target.value)}
                                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-4 focus:ring-primary/10 transition-all outline-none"
                                    placeholder="Enter strategy name"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Target Asset/Ticker</label>
                                <input
                                    type="text"
                                    list="strategy-ticker-options"
                                    value={newStratSymbol}
                                    onChange={(e) => setNewStratSymbol(e.target.value.toUpperCase())}
                                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-4 focus:ring-primary/10 transition-all outline-none"
                                    placeholder="Select or type symbol"
                                />
                                <datalist id="strategy-ticker-options">
                                    {symbolOptions.map((item) => (
                                        <option key={`${item.exchange}-strat-${item.symbol}`} value={item.symbol}>
                                            {item.exchange}
                                        </option>
                                    ))}
                                </datalist>
                            </div>

                            <div className="bg-slate-900 p-4 rounded-2xl text-white/80 space-y-3">
                                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                    <span className="opacity-60">Execution Tier</span>
                                    <span className="text-primary">ULTRA-LOW LATENCY</span>
                                </div>
                                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                    <span className="opacity-60">Risk Profile</span>
                                    <span className="text-green-400 font-bold">BALANCED</span>
                                </div>
                            </div>

                            <button
                                onClick={handleLaunchStrategy}
                                disabled={provisioning}
                                className="w-full py-4 bg-primary text-white rounded-2xl font-black uppercase tracking-[0.2em] shadow-xl shadow-primary/20 hover:opacity-95 transition-all flex items-center justify-center gap-3 active:scale-95"
                            >
                                {provisioning ? <Loader2 className="animate-spin" size={18} /> : <Zap size={18} fill="currentColor" />}
                                {provisioning ? 'Initializing Node...' : 'Confirm Deployment'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <Card className="p-6 border-slate-200 shadow-sm col-span-1 lg:col-span-3">
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-slate-900 rounded-lg text-primary">
                                <Activity size={20} />
                            </div>
                            <div>
                                <h3 className="font-black text-slate-900 uppercase text-xs tracking-widest">Manual Order Ticket</h3>
                                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">Direct Exchange Access</p>
                            </div>
                        </div>
                        {user?.trading_mode === 'AUTO' && (
                            <div className="flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-lg animate-pulse">
                                <Activity size={12} className="text-primary" />
                                <span className="text-[10px] font-black text-primary uppercase tracking-widest">AI observing order book...</span>
                            </div>
                        )}
                    </div>

                    <div data-testid="manual-order-ticket" className={`flex flex-col md:flex-row gap-6 items-end ${user?.trading_mode === 'AUTO' ? 'opacity-30 grayscale pointer-events-none' : ''}`}>
                        <div className="flex-1 w-full space-y-2">
                            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Asset Ticker</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    list="ticker-options"
                                    value={orderTicker}
                                    onChange={(e) => setOrderTicker(e.target.value.toUpperCase())}
                                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                                    placeholder="Type or select a symbol"
                                />
                                <datalist id="ticker-options">
                                    {symbolOptions.map((item) => (
                                        <option key={`${item.exchange}-${item.symbol}`} value={item.symbol}>
                                            {item.exchange}
                                        </option>
                                    ))}
                                </datalist>
                            </div>
                            <div className="flex flex-wrap gap-2 mt-2">
                                {symbolOptions.slice(0, 6).map((item) => (
                                    <button
                                        key={`${item.exchange}-quick-${item.symbol}`}
                                        type="button"
                                        onClick={() => setOrderTicker(item.symbol)}
                                        className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${orderTicker === item.symbol ? 'bg-primary/10 border-primary text-primary' : 'bg-white border-slate-200 text-slate-500 hover:text-slate-700'}`}
                                    >
                                        {item.exchange}:{item.symbol}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="w-full md:w-32 space-y-2">
                            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Units</label>
                            <input
                                type="number"
                                value={orderQty}
                                onChange={(e) => setOrderQty(parseInt(e.target.value) || 0)}
                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                                placeholder="Qty"
                            />
                        </div>
                        <div className="flex gap-3 w-full md:w-auto">
                            <button
                                onClick={() => handleManualTrade('BUY')}
                                disabled={executing}
                                className="px-6 py-3.5 bg-green-600 text-white rounded-xl font-black text-sm uppercase tracking-widest hover:bg-green-700 transition-all shadow-lg shadow-green-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                {executing ? <Loader2 size={16} className="animate-spin" /> : <TrendingUp size={16} />}
                                Buy
                            </button>
                            <button
                                onClick={() => handleManualTrade('SELL')}
                                disabled={executing}
                                className="px-6 py-3.5 bg-red-600 text-white rounded-xl font-black text-sm uppercase tracking-widest hover:bg-red-700 transition-all shadow-lg shadow-red-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                {executing ? <Loader2 size={16} className="animate-spin" /> : <TrendingDown size={16} />}
                                Sell
                            </button>
                            <button
                                onClick={addToBasket}
                                className="px-4 py-3.5 bg-slate-900 text-white rounded-xl font-black text-sm uppercase tracking-widest hover:bg-slate-800 transition-all"
                            >
                                <Target size={16} />
                            </button>
                        </div>
                    </div>
                </Card>
                
                <Card className="p-6 border-slate-200 shadow-sm">
                    <div className="flex flex-col h-full">
                        <h3 className="font-black text-slate-900 uppercase text-xs tracking-widest mb-4">Quick Actions</h3>
                        
                        <div className="space-y-3 flex-1">
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
                            
                            <button className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors">
                                <div className="flex items-center gap-2">
                                    <Target size={16} className="text-primary" />
                                    <span className="font-black text-slate-900">Risk Controls</span>
                                </div>
                                <p className="text-xs text-slate-500 mt-1">Portfolio risk management</p>
                            </button>
                            
                            <button className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-left hover:bg-slate-100 transition-colors">
                                <div className="flex items-center gap-2">
                                    <Activity size={16} className="text-primary" />
                                    <span className="font-black text-slate-900">Live Feed</span>
                                </div>
                                <p className="text-xs text-slate-500 mt-1">Real-time market data</p>
                            </button>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Active Strategies */}
            <Card className="p-6 border-slate-200 shadow-sm">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-black text-slate-900 uppercase tracking-widest">Active Strategies</h3>
                    <span className="text-sm font-black bg-primary/10 text-primary px-3 py-1 rounded-full">
                        {strategies.length} running
                    </span>
                </div>
                
                {strategies.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {strategies.map((strategy) => (
                            <div key={strategy.id} className="p-4 border border-slate-200 rounded-xl bg-white">
                                <div className="flex justify-between items-start mb-3">
                                    <h4 className="font-black text-slate-900">{strategy.name}</h4>
                                    <span className={`px-2 py-1 rounded-full text-xs font-black uppercase ${
                                        strategy.status === 'RUNNING' 
                                            ? 'bg-green-100 text-green-700' 
                                            : 'bg-amber-100 text-amber-700'
                                    }`}>
                                        {strategy.status}
                                    </span>
                                </div>
                                
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Symbol:</span>
                                        <span className="font-black">{strategy.symbol}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">PnL:</span>
                                        <span className={`font-black ${strategy.pnl >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                                            {strategy.pnl >= 0 ? '+' : ''}{strategy.pnl.toFixed(2)}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-500">Trades:</span>
                                        <span className="font-black">{strategy.total_trades}</span>
                                    </div>
                                </div>
                                
                                <div className="mt-4 flex gap-2">
                                    <button className="flex-1 py-2 bg-slate-100 text-slate-700 rounded-lg text-xs font-black uppercase tracking-widest hover:bg-slate-200 transition-colors">
                                        Pause
                                    </button>
                                    <button className="flex-1 py-2 bg-primary text-white rounded-lg text-xs font-black uppercase tracking-widest hover:opacity-90 transition-opacity">
                                        Stats
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <Activity size={48} className="mx-auto text-slate-300 mb-4" />
                        <h4 className="font-black text-slate-500 mb-2">No Active Strategies</h4>
                        <p className="text-sm text-slate-400">Launch a strategy to begin automated trading</p>
                    </div>
                )}
            </Card>

            {/* Order Basket Modal */}
            {showBasketModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md">
                    <div className="bg-white rounded-3xl p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-black text-slate-900">Order Basket</h3>
                            <button 
                                onClick={() => setShowBasketModal(false)}
                                className="text-slate-400 hover:text-slate-600"
                            >
                                <X size={24} />
                            </button>
                        </div>
                        
                        {basket.length > 0 ? (
                            <>
                                <div className="space-y-3 mb-6">
                                    {basket.map((order, index) => (
                                        <div key={order.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-xl">
                                            <div>
                                                <span className="font-black text-slate-900">{order.symbol}</span>
                                                <span className="text-sm text-slate-500 ml-2">{order.side}</span>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <span className="font-black">{order.quantity} @ INR {order.price}</span>
                                                <button 
                                                    onClick={() => setBasket(prev => prev.filter((_, i) => i !== index))}
                                                    className="text-red-500 hover:text-red-700"
                                                >
                                                    <X size={16} />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                
                                <div className="flex justify-between items-center mb-6 p-4 bg-slate-50 rounded-xl">
                                    <span className="font-black text-slate-900">Total Value:</span>
                                    <span className="text-xl font-black text-slate-900">INR {basketTotal.toFixed(2)}</span>
                                </div>
                                
                                <div className="flex justify-end gap-3">
                                    <button
                                        onClick={() => setShowBasketModal(false)}
                                        className="px-6 py-3 border border-slate-200 text-slate-700 rounded-xl font-black text-sm uppercase tracking-widest hover:bg-slate-50 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={executeBasket}
                                        disabled={executingBasket}
                                        className="px-6 py-3 bg-primary text-white rounded-xl font-black text-sm uppercase tracking-widest hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
                                    >
                                        {executingBasket ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
                                        Execute Basket
                                    </button>
                                </div>
                            </>
                        ) : (
                            <div className="text-center py-8">
                                <ShoppingBag size={48} className="mx-auto text-slate-300 mb-4" />
                                <h4 className="font-black text-slate-500 mb-2">Basket is Empty</h4>
                                <p className="text-sm text-slate-400">Add orders to your basket to execute them together</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Trading Logic Console */}
            <Card className="p-6 border-slate-200 shadow-sm">
                <h3 className="text-lg font-black text-slate-900 uppercase tracking-widest mb-6">Intelligence Log</h3>
                
                <div className="space-y-3 max-h-64 overflow-y-auto">
                    {logs.map((log) => (
                        <div key={log.id} className="flex gap-3 text-xs font-bold text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100">
                            <span className="text-slate-400 font-mono">[{log.time}]</span>
                            <span className={`font-black uppercase tracking-widest ${
                                log.type === 'system' ? 'text-indigo-600' : 
                                log.type === 'logic' ? 'text-primary' : 
                                'text-green-600'
                            }`}>
                                {log.type.toUpperCase()}:
                            </span>
                            <span className="text-slate-700">{log.msg}</span>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
    );
}


