import React, { useState, useEffect, useMemo } from 'react';
import { Card } from "../components/ui/card";
import { Play, Pause, RefreshCcw, Zap, Target, TrendingUp, TrendingDown, ArrowUpRight, Shield, Loader2, Lock, Unlock, Settings2, X, ArrowRight, Activity } from 'lucide-react';
import { fetchStrategies, fetchProjections, fetchUser, updateUser, fetchPortfolioHistory, fetchPortfolioSummary, fetchExchangeStatus, executeTrade, fetchHoldings, launchStrategy, socket, depositFunds } from "../services/api";

import { useUser } from "../context/UserContext";
import { useAppData } from "../context/AppDataContext";
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
        toggleTradingMode: appToggleTradingMode,
        refreshAllData
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
            await appToggleTradingMode();
        } finally {
            setToggling(false);
        }
    };

    const handleManualTrade = async (action) => {
        if (!user || user.trading_mode !== 'MANUAL') return;
        if (!orderTicker || orderQty <= 0) {
            setTradeStatus({ type: 'error', msg: 'Select a valid ticker and quantity.' });
            setTimeout(() => setTradeStatus(null), 4000);
            return;
        }

        setExecuting(true);
        try {
            const normalizedSymbol = orderTicker.includes(':') ? orderTicker.split(':').pop() : orderTicker;
            const priceFromMarket = (marketMovers || []).find(m => m.symbol === normalizedSymbol)?.price;
            const tradeData = {
                symbol: normalizedSymbol,
                action: action, // BUY or SELL
                price: priceFromMarket || 2450.00, // Mock live price fallback
                quantity: orderQty,
                type: 'MANUAL',
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

    const getPriceForSymbol = (symbol) => {
        const normalized = symbol.includes(':') ? symbol.split(':').pop() : symbol;
        const priceFromMarket = (marketMovers || []).find(m => m.symbol === normalized)?.price;
        return priceFromMarket || 2450.00;
    };

    const addToBasket = () => {
        if (!orderTicker || orderQty <= 0) {
            setTradeStatus({ type: 'error', msg: 'Select a valid ticker and quantity.' });
            setTimeout(() => setTradeStatus(null), 4000);
            return;
        }
        const normalized = orderTicker.includes(':') ? orderTicker.split(':').pop() : orderTicker;
        const price = getPriceForSymbol(normalized);
        setBasket(prev => ([...prev, {
            id: Date.now(),
            symbol: normalized,
            quantity: orderQty,
            price,
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
        if (!user || user.trading_mode !== 'MANUAL') return;
        if (basket.length === 0) return;

        const cashBalance = summary?.cash_balance || 0;
        if (basketTotal > cashBalance) {
            const shortfall = basketTotal - cashBalance;
            setTopupAmount(Math.ceil(shortfall));
            setShowTopupModal(true);
            return;
        }

        setExecuting(true);
        try {
            for (const item of basket) {
                await executeTrade(user.id, {
                    symbol: item.symbol,
                    action: item.side,
                    price: item.price,
                    quantity: item.quantity,
                    type: 'MANUAL',
                    decision_logic: `Basket order: ${item.side} ${item.quantity} ${item.symbol}`
                });
            }
            await refreshAllData();
            const updatedHoldings = await fetchHoldings(user.id);
            setActiveHoldings(updatedHoldings);
            setBasket([]);
            setTradeStatus({ type: 'success', msg: 'Basket executed successfully.' });
            setTimeout(() => setTradeStatus(null), 4000);
        } catch (err) {
            console.error('Basket trade failed:', err);
            setTradeStatus({ type: 'error', msg: 'Basket execution failed.' });
            setTimeout(() => setTradeStatus(null), 4000);
        } finally {
            setExecuting(false);
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
                pnl: '+? 0.00',
                trades: '0'
            };
            const result = await launchStrategy(contextUser.id, stratData);
            if (result) {
                setStrategies(prev => [...prev, result]);
                setShowLaunchModal(false);
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

        const fromHoldings = (activeHoldings || []).map(h => ({ symbol: h.symbol, exchange: h.exchange || 'NSE' }));
        const fromWatchlist = (watchlist || []).map(w => ({ symbol: w.symbol, exchange: w.exchange || 'NSE' }));
        const fromMovers = (marketMovers || []).map(m => ({ symbol: m.symbol, exchange: m.exchange || 'NSE' }));
        const fromProjections = (projections || []).map(p => ({ symbol: p.ticker, exchange: 'NSE' }));

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
                        {user?.trading_mode === 'AUTO' ? <Shield size={14} className="animate-pulse" /> : <Lock size={14} />}
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
                        {user?.trading_mode === 'MANUAL' ? <Unlock size={14} className="animate-bounce" /> : <Shield size={14} />}
                        Manual Mode
                    </button>
                </div>

                <div className="h-10 w-[1px] bg-slate-100 hidden md:block mx-4" />

                <div className="flex flex-col items-end mr-4">
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Exchange Status</span>
                    <div className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-[10px] font-black text-slate-900">{exchangeStatus.exchange || 'NSE'} {exchangeStatus.latency}</span>
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
                    <Card className="w-full max-w-md bg-white p-8 rounded-3xl shadow-2xl relative overflow-hidden">
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
                    </Card>
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
                                onChange={(e) => setOrderQty(parseInt(e.target.value))}
                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm font-black text-slate-900 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                            />
                        </div>
                        <div className="flex gap-2 w-full md:w-auto">
                            <button
                                data-testid="manual-buy-button"
                                onClick={() => handleManualTrade('BUY')}
                                disabled={executing}
                                className="flex-1 md:flex-none bg-green-600 text-white px-8 py-3.5 rounded-xl font-black text-xs uppercase tracking-widest hover:bg-green-700 transition-all shadow-lg shadow-green-600/20 active:scale-95 flex items-center justify-center gap-2"
                            >
                                {executing ? <Loader2 size={16} className="animate-spin" /> : <TrendingUp size={16} />}
                                Buy
                            </button>
                            <button
                                type="button"
                                onClick={addToBasket}
                                disabled={executing}
                                className="flex-1 md:flex-none bg-slate-900 text-white px-6 py-3.5 rounded-xl font-black text-xs uppercase tracking-widest hover:bg-slate-800 transition-all shadow-lg shadow-slate-900/20 active:scale-95"
                            >
                                Add to Basket
                            </button>
                            <button
                                data-testid="manual-sell-button"
                                onClick={() => handleManualTrade('SELL')}
                                disabled={executing}
                                className="flex-1 md:flex-none bg-red-600 text-white px-8 py-3.5 rounded-xl font-black text-xs uppercase tracking-widest hover:bg-red-700 transition-all shadow-lg shadow-red-600/20 active:scale-95 flex items-center justify-center gap-2"
                            >
                                {executing ? <Loader2 size={16} className="animate-spin" /> : <TrendingDown size={16} />}
                                Sell
                            </button>
                        </div>
                        {tradeStatus && (
                            <div className={`w-full mt-4 p-3 rounded-xl border text-[10px] font-black uppercase tracking-widest animate-in fade-in slide-in-from-top-2 ${tradeStatus.type === 'success' ? 'bg-green-50 border-green-100 text-green-600' : 'bg-red-50 border-red-100 text-red-600'
                                }`}>
                                {tradeStatus.msg}
                            </div>
                        )}
                    </div>
                    {user?.trading_mode === 'AUTO' && (
                        <div className="mt-3 text-[10px] font-black uppercase tracking-widest text-slate-400">
                            Manual trading is disabled in AUTO mode. Switch to MANUAL to place orders.
                        </div>
                    )}
                    {user?.trading_mode === 'MANUAL' && (
                        <div className="mt-4 w-full">
                            <button
                                type="button"
                                onClick={() => setShowBasketModal(true)}
                                className="px-4 py-2 rounded-lg bg-slate-50 border border-slate-200 text-[10px] font-black uppercase tracking-widest text-slate-600 hover:bg-slate-100"
                            >
                                Basket ({basket.length}) - ? {basketTotal.toLocaleString()}
                            </button>
                        </div>
                    )}
                </Card>

                <Card className="p-6 border-slate-200 shadow-sm flex flex-col justify-center items-center text-center bg-slate-50 border-dashed">
                    <div className="h-12 w-12 rounded-2xl bg-white shadow-md flex items-center justify-center text-indigo-600 mb-3">
                        <ArrowRight size={20} />
                    </div>
                    <h3 className="text-xs font-black text-slate-900 uppercase tracking-widest mb-1">Hold Status</h3>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest leading-tight">No active orders pending manual confirmation.</p>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Active Automated Strategies */}
                <div className="lg:col-span-8 flex flex-col gap-8">
                    <div className="space-y-6 relative group">
                        <h2 data-testid="strategies-heading" className="text-xl font-black text-slate-900 px-1 font-heading uppercase tracking-widest text-sm">Active Automated Strategies</h2>

                        {user?.trading_mode === 'AUTO' && (
                            <div className="p-4 rounded-2xl bg-primary/5 border border-primary/20 text-[10px] font-black uppercase tracking-widest text-primary flex items-center gap-2">
                                <Shield size={12} className="animate-pulse" />
                                Steward AI autopilot active. Strategy controls are read-only.
                            </div>
                        )}

                        <div data-testid="automated-strategies-list" className="grid grid-cols-1 gap-4">
                            {Array.isArray(strategies) && strategies.length > 0 ? strategies.map((strat) => (
                                <Card key={strat.id} className="p-6 border-slate-100 shadow-sm hover:border-primary/30 transition-all group bg-white">
                                    <div className="flex items-start justify-between gap-4">
                                        <div>
                                            <h3 className="text-sm font-black text-slate-900">{strat.name}</h3>
                                            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">
                                                {strat.symbol || 'NSE'} - {strat.execution_mode || 'PAPER_TRADING'}
                                            </p>
                                        </div>
                                        <span className={`px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${strat.status === 'RUNNING' ? 'bg-green-100 text-green-700' : strat.status === 'PAUSED' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'}`}>
                                            {strat.status || 'IDLE'}
                                        </span>
                                    </div>
                                    <div className="grid grid-cols-3 gap-4 mt-4">
                                        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                                            <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">PnL</p>
                                            <p className="text-sm font-black text-slate-900">{strat.pnl || '? 0.00'}</p>
                                        </div>
                                        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                                            <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Drawdown</p>
                                            <p className="text-sm font-black text-slate-900">{strat.drawdown ?? 0}%</p>
                                        </div>
                                        <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                                            <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Mode</p>
                                            <p className="text-sm font-black text-slate-900">{strat.execution_mode || 'PAPER'}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between mt-4">
                                        <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-400">
                                            <Activity size={12} className="text-primary" />
                                            Live status feed
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                type="button"
                                                disabled={user?.trading_mode === 'AUTO'}
                                                className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest ${user?.trading_mode === 'AUTO' ? 'bg-slate-100 text-slate-400' : 'bg-green-100 text-green-700 hover:bg-green-200'}`}
                                            >
                                                <Play size={12} className="inline mr-1" />
                                                Run
                                            </button>
                                            <button
                                                type="button"
                                                disabled={user?.trading_mode === 'AUTO'}
                                                className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest ${user?.trading_mode === 'AUTO' ? 'bg-slate-100 text-slate-400' : 'bg-amber-100 text-amber-700 hover:bg-amber-200'}`}
                                            >
                                                <Pause size={12} className="inline mr-1" />
                                                Pause
                                            </button>
                                        </div>
                                    </div>
                                </Card>
                            )) : (
                                <div className="p-12 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">No Active Strategies Provisioned</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Agent Thought Stream */}
                    <Card className="border-slate-200 shadow-sm overflow-hidden bg-white">
                        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
                            <div className="flex items-center gap-2">
                                <Activity size={14} className="text-primary animate-pulse" />
                                <span className="text-[10px] font-black uppercase tracking-widest text-slate-900">Agent Thought Stream</span>
                            </div>
                            <span className="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Live Telemetry</span>
                        </div>
                        <div className="p-4 space-y-3 h-[240px] overflow-y-auto font-mono scrollbar-hide">
                            {logs.map((log) => (
                                <div key={log.id} className="flex gap-3 text-[10px] animate-in slide-in-from-left-2 duration-300">
                                    <span className="text-slate-400 shrink-0">[{log.time}]</span>
                                    <span className={`font-bold ${log.type === 'logic' ? 'text-indigo-600' : log.type === 'system' ? 'text-slate-500' : 'text-primary'
                                        }`}>
                                        {log.type.toUpperCase()}:
                                    </span>
                                    <span className="text-slate-700">{log.msg}</span>
                                </div>
                            ))}
                        </div>
                    </Card>
                </div>

                {/* AI Next Day Projections */}
                <div className="lg:col-span-4 space-y-6">
                    <h2 className="text-xl font-black text-slate-900 px-1 font-heading uppercase tracking-widest text-sm">Next-Day Projections</h2>
                    <Card className="p-6 border-primary/20 bg-green-50/30 shadow-xl shadow-primary/5">
                        <div className="flex items-center gap-2 mb-6">
                            <TrendingUp size={18} className="text-primary" />
                            <span className="text-[10px] font-black text-primary uppercase tracking-[0.2em]">Alpha Recommendation</span>
                        </div>

                        <div className="space-y-4">
                            {projections.map((proj, i) => (
                                <div key={i} className="p-4 rounded-2xl bg-white border border-slate-100 shadow-sm group hover:border-primary/50 transition-all cursor-pointer">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-black text-slate-900">{proj.ticker}</span>
                                        <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${proj.move_prediction.startsWith('+') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                            }`}>{proj.move_prediction}</span>
                                    </div>
                                    <p className="text-[10px] text-slate-500 font-bold leading-relaxed">{proj.logic}</p>
                                    <div className="mt-3 flex items-center justify-between">
                                        <span className="text-[9px] font-black bg-slate-900 text-white px-2 py-0.5 rounded-md">{proj.action}</span>
                                        <ArrowUpRight size={14} className="text-slate-300 group-hover:text-primary transition-colors" />
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-6 p-4 rounded-2xl bg-slate-900 text-white border-none">
                            <h4 className="text-xs font-black uppercase tracking-widest mb-2 flex items-center gap-2">
                                <Shield size={14} className="text-primary" />
                                Logic Validation
                            </h4>
                            <p className="text-[9px] text-slate-400 font-medium leading-relaxed">
                                Recommendations are based on 14-day trailing sentiment analysis and real-time order flow data.
                                <span className="text-primary font-black ml-1">Live data feed active.</span>
                            </p>
                        </div>
                    </Card>
                </div>
            </div>

            <Card className="p-10 bg-[#0A2A4D] text-white border-none shadow-2xl overflow-hidden relative">
                <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="max-w-xl">
                        <div className="flex items-center gap-2 mb-6">
                            <span className="px-3 py-1 rounded-full bg-primary text-[10px] font-black uppercase tracking-widest">Global Watcher Alpha</span>
                            <span className="text-white/40 text-[10px] font-bold leading-none uppercase tracking-widest">Cluster Node: AP-SOUTH-1 (Mumbai)</span>
                        </div>
                        <h3 className="text-3xl font-black mb-4 font-heading leading-tight italic">"{appStewardPrediction?.prediction || "Market intelligence syncing..."}"</h3>
                        <p className="text-slate-300 text-[10px] font-black leading-relaxed mb-8 uppercase tracking-[0.2em] flex items-center gap-2">
                            <span className="h-2 w-2 bg-green-500 rounded-full animate-ping" />
                            Live Steward Forecast Stream
                        </p>
                        <div className="flex flex-wrap gap-4">
                            <button className="px-8 py-3 bg-white text-slate-900 rounded-xl font-black text-xs hover:scale-105 transition-transform uppercase tracking-widest shadow-lg">Emergency Stop All</button>
                            <button className="px-8 py-3 bg-white/10 text-white rounded-xl font-black text-xs border border-white/20 hover:bg-white/20 transition-all uppercase tracking-widest">View Decision Tree</button>
                        </div>
                    </div>

                    <div className="hidden lg:grid grid-cols-2 gap-4 flex-shrink-0">
                        <div className="p-6 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
                            <p className="text-[10px] text-white/40 font-black uppercase tracking-widest mb-1">HFT Latency</p>
                            <p className="text-2xl font-black text-white">42ms</p>
                        </div>
                        <div className="p-6 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
                            <p className="text-[10px] text-white/40 font-black uppercase tracking-widest mb-1">Confidence</p>
                            <p className="text-2xl font-black text-green-400">92%</p>
                        </div>
                    </div>
                </div>
                {/* Visual accents */}
                <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-primary/10 to-transparent pointer-events-none" />
                <div className="absolute -bottom-24 -right-24 h-64 w-64 bg-primary/20 rounded-full blur-[100px] pointer-events-none" />
            </Card>

            {showBasketModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
                    <Card className="w-full max-w-xl bg-white p-6 rounded-3xl shadow-2xl relative">
                        <button
                            onClick={() => setShowBasketModal(false)}
                            className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            <X size={18} />
                        </button>
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Order Basket</h3>
                        {basket.length === 0 ? (
                            <div className="text-xs text-slate-500">No orders in basket.</div>
                        ) : (
                            <div className="space-y-3">
                                {basket.map(item => (
                                    <div key={item.id} className="flex items-center justify-between text-xs font-bold text-slate-700 bg-slate-50 border border-slate-100 rounded-xl px-3 py-2">
                                        <span>{item.symbol}</span>
                                        <span>{item.quantity} @ ? {item.price}</span>
                                        <span className="text-primary">{item.side}</span>
                                        <button
                                            onClick={() => removeFromBasket(item.id)}
                                            className="text-[9px] font-black uppercase tracking-widest text-red-500"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                        <div className="mt-4 flex items-center justify-between">
                            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Total</span>
                            <span className="text-sm font-black text-slate-900">? {basketTotal.toLocaleString()}</span>
                        </div>
                        <div className="mt-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowBasketModal(false)}
                                className="px-4 py-2 text-[10px] font-black uppercase tracking-widest bg-slate-100 text-slate-600 rounded-lg"
                            >
                                Close
                            </button>
                            <button
                                onClick={() => { setShowBasketModal(false); executeBasket(); }}
                                className="px-4 py-2 text-[10px] font-black uppercase tracking-widest bg-primary text-white rounded-lg"
                            >
                                Execute Basket
                            </button>
                        </div>
                    </Card>
                </div>
            )}

            {showTopupModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
                    <Card className="w-full max-w-md bg-white p-6 rounded-3xl shadow-2xl relative">
                        <button
                            onClick={() => setShowTopupModal(false)}
                            className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            <X size={18} />
                        </button>
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Insufficient Funds</h3>
                        <p className="text-xs text-slate-600">You need additional ? {topupAmount.toLocaleString()} to execute this basket.</p>
                        <div className="mt-4">
                            <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Top-up Amount (₹)</label>
                            <input
                                type="number"
                                value={topupAmount}
                                onChange={(e) => setTopupAmount(parseInt(e.target.value || '0'))}
                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm font-black"
                            />
                        </div>
                        <div className="mt-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowTopupModal(false)}
                                className="px-4 py-2 text-[10px] font-black uppercase tracking-widest bg-slate-100 text-slate-600 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={async () => {
                                    await refreshAllData();
                                    await fetchPortfolioSummary(user.id);
                                    await depositFunds(user.id, topupAmount);
                                    setShowTopupModal(false);
                                    executeBasket();
                                }}
                                className="px-4 py-2 text-[10px] font-black uppercase tracking-widest bg-primary text-white rounded-lg"
                            >
                                Add Funds & Execute
                            </button>
                        </div>
                    </Card>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-2 p-6 border-slate-200 shadow-sm bg-white">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h3 className="text-sm font-black uppercase tracking-widest text-slate-900">Live Research Stream</h3>
                            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">Macro + sector notes</p>
                        </div>
                        <span className="text-[10px] font-black text-primary uppercase">Streaming</span>
                    </div>
                    <div className="space-y-3">
                        {(marketResearch?.headlines || []).map((h, i) => (
                            <div key={i} className="p-3 rounded-xl border border-slate-100 bg-slate-50 text-xs font-bold text-slate-800">
                                {h}
                            </div>
                        ))}
                    </div>
                </Card>

                <Card className="p-6 border-slate-200 shadow-sm bg-white">
                    <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Signal Bias</h3>
                    <div className="space-y-3">
                        {(marketResearch?.watchlist || []).map((w, i) => (
                            <div key={i} className="flex items-center justify-between text-xs">
                                <span className="font-black text-slate-800">{w.symbol}</span>
                                <span className={`text-[9px] font-black px-2 py-0.5 rounded-full ${w.bias === 'BUY' ? 'bg-green-100 text-green-700' : w.bias === 'SELL' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'}`}>
                                    {w.bias}
                                </span>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
}


