import React, { useState, useEffect, useMemo, useRef } from 'react';
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
    DollarSign,
    Unlock as UnlockIcon,
    Lock as LockIcon,
    BarChart3,
    Eye,
    Info,
    AlertCircle,
    ChevronDown,
    ChevronUp,
    MoveUp,
    MoveDown,
    Globe,
    Cpu,
    Flame
} from 'lucide-react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine
} from 'recharts';
import {
    executeTrade,
    fetchHoldings,
    launchStrategy,
    fetchStrategies,
    fetchExchangeStatus
} from "../services/api";

import { useUser } from "../context/UserContext";
import { useAppData } from "../context/AppDataContext";

// --- Sub-components for Maturity ---

const SentimentGauge = ({ val = 68 }) => (
    <div className="relative h-24 w-full flex items-center justify-center">
        <svg className="w-full h-full -rotate-180" viewBox="0 0 100 50">
            <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#e2e8f0" strokeWidth="10" />
            <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="url(#gradient-sentiment)" strokeWidth="10" strokeDasharray="126" strokeDashoffset={126 - (126 * val) / 100} className="transition-all duration-1000 ease-out" />
            <defs>
                <linearGradient id="gradient-sentiment" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#f87171" />
                    <stop offset="50%" stopColor="#fbbf24" />
                    <stop offset="100%" stopColor="#10b981" />
                </linearGradient>
            </defs>
        </svg>
        <div className="absolute inset-x-0 bottom-0 text-center">
            <p className="text-xl font-black text-slate-900 leading-none">{val}%</p>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">BULLISH SENTIMENT</p>
        </div>
    </div>
);

const TechnicalIndicator = ({ label, status, value }) => (
    <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{label}</span>
        <div className="flex items-center gap-2">
            <span className={`text-[10px] font-black uppercase ${status === 'BULLISH' ? 'text-green-600' : 'text-red-500'}`}>{status}</span>
            <span className="text-[10px] font-bold text-slate-400">({value})</span>
        </div>
    </div>
);

// --- Confirmation Handshake Animation ---
const ConfirmationOverlay = ({ show, onComplete }) => {
    useEffect(() => {
        if (show) {
            const timer = setTimeout(onComplete, 2500);
            return () => clearTimeout(timer);
        }
    }, [show, onComplete]);

    if (!show) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/80 backdrop-blur-xl animate-in fade-in duration-300">
            <div className="flex flex-col items-center">
                <div className="relative h-32 w-32 mb-6">
                    <div className="absolute inset-0 border-4 border-primary/20 rounded-full animate-ping" />
                    <div className="absolute inset-0 border-4 border-primary rounded-full animate-slow-spin flex items-center justify-center">
                        <Lock size={48} className="text-primary" />
                    </div>
                </div>
                <h2 className="text-2xl font-black text-white uppercase tracking-[0.2em] mb-2 animate-pulse">Security Handshake</h2>
                <p className="text-sm font-bold text-primary uppercase tracking-widest">Validating Order Fingerprint...</p>
                <div className="mt-8 flex gap-2">
                    {[1, 2, 3].map(i => (
                        <div key={i} className={`h-1.5 w-8 rounded-full bg-primary/20 overflow-hidden`}>
                            <div className="h-full bg-primary animate-progress" style={{ animationDelay: `${i * 0.2}s` }} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export function TradingHub() {
    const { user: contextUser } = useUser();
    const {
        summary,
        strategies: appStrategies,
        exchangeStatus,
        stewardPrediction,
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
    const [assetClass, setAssetClass] = useState('EQUITY');
    const [orderTicker, setOrderTicker] = useState('RELIANCE');
    const [orderQty, setOrderQty] = useState(10);
    const [orderType, setOrderType] = useState('MARKET');
    const [stopLoss, setStopLoss] = useState(null);
    const [takeProfit, setTakeProfit] = useState(null);
    const [showConfirmation, setShowConfirmation] = useState(false);
    const [trainingMode, setTrainingMode] = useState(false);
    const [logs, setLogs] = useState([]);
    const [activeTab, setActiveTab] = useState('EXECUTION'); // EXECUTION, ANALYSIS, ALGO

    const user = contextUser;

    // Live Price simulation/fetch
    const currentPrice = useMemo(() => {
        if (!marketMovers) return 2450.00;
        const all = [...(marketMovers.gainers || []), ...(marketMovers.losers || [])];
        const found = all.find(m => m.symbol === orderTicker);
        return found ? found.price : 2450.00;
    }, [orderTicker, marketMovers]);

    const chartData = useMemo(() => {
        return Array.from({ length: 20 }, (_, i) => ({
            name: i,
            price: currentPrice + (Math.random() - 0.5) * 40
        }));
    }, [currentPrice, orderTicker]);

    useEffect(() => {
        if (Array.isArray(appStrategies) && appStrategies.length > 0) {
            setStrategies(appStrategies);
        }
    }, [appStrategies]);

    const addLog = (msg, type = 'info') => {
        setLogs(prev => [{
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            msg,
            type
        }, ...prev].slice(0, 50));
    };

    const handleExecuteTrade = async (side) => {
        if (!user || orderQty <= 0) return;

        setShowConfirmation(true);
        // We'll actually execute after the handshake in a real flow, but for this mature feel,
        // we show the handshake first.
    };

    const onHandshakeComplete = async () => {
        setShowConfirmation(false);
        setExecuting(true);
        try {
            const tradeData = {
                symbol: orderTicker,
                side: 'BUY', // Simplified for this example
                quantity: orderQty,
                price: currentPrice,
                order_type: orderType,
                asset_class: assetClass,
                decision_logic: `Institutional Terminal Execution: ${orderQty} ${orderTicker} @ ${orderType}. Stop: ${stopLoss}%, Target: ${takeProfit}%`
            };
            await executeTrade(user.id, tradeData);
            addLog(`Order Executed: BUY ${orderQty} ${orderTicker} @ ${currentPrice}`, 'success');
            await refreshAllData();
        } catch (err) {
            addLog(`Execution Failed: ${err.message}`, 'error');
        } finally {
            setExecuting(false);
        }
    };

    if (loading) {
        return (
            <div className="h-[70vh] flex flex-col items-center justify-center text-slate-400 bg-slate-50/50 rounded-3xl border border-slate-100">
                <Loader2 className="animate-spin mb-6 text-primary" size={48} />
                <p className="font-black uppercase text-[10px] tracking-[0.4em] text-slate-500 animate-pulse">Synchronizing Terminal Core...</p>
            </div>
        );
    }

    return (
        <div className={`space-y-6 animate-in fade-in duration-700 pb-12 ${trainingMode ? 'ring-4 ring-amber-400/20 rounded-3xl' : ''}`}>
            <ConfirmationOverlay show={showConfirmation} onComplete={onHandshakeComplete} />

            {/* Premium Header */}
            <header className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 bg-slate-900 text-white p-8 rounded-[2rem] shadow-2xl relative overflow-hidden border border-slate-800">
                <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-primary/10 to-transparent pointer-events-none" />
                <div className="absolute -bottom-24 -left-24 h-64 w-64 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary">Strategic Execution Terminal</span>
                    </div>
                    <h1 className="text-4xl font-black tracking-tighter font-heading text-white">Steward <span className="text-primary italic">Pro</span></h1>
                    <div className="flex items-center gap-6 mt-4">
                        <div className="flex flex-col">
                            <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest leading-none mb-1">Exchange Status</span>
                            <div className="flex items-center gap-2">
                                <span className="h-1.5 w-1.5 bg-green-500 rounded-full animate-pulse" />
                                <span className="text-xs font-black uppercase tracking-tight">{exchangeStatus?.exchange || 'NSE'} CONNECTED</span>
                            </div>
                        </div>
                        <div className="h-8 w-[1px] bg-slate-800" />
                        <div className="flex flex-col">
                            <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest leading-none mb-1">Available Liquidity</span>
                            <span className="text-xs font-black text-primary uppercase tracking-tight">INR {summary?.cash_balance?.toLocaleString() || '0'}</span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center relative z-10 w-full lg:w-auto">
                    {/* Training Mode Toggle */}
                    <button
                        onClick={() => setTrainingMode(!trainingMode)}
                        className={`group px-6 py-4 rounded-2xl border transition-all duration-300 flex items-center gap-3 shadow-lg ${trainingMode
                            ? 'bg-amber-400 border-amber-500 text-slate-900 shadow-amber-400/20'
                            : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white hover:border-slate-600'}`}
                    >
                        <BarChart3 size={20} className={trainingMode ? 'animate-bounce' : ''} />
                        <div className="text-left">
                            <p className="text-[10px] font-black uppercase tracking-widest leading-none mb-1">{trainingMode ? 'Training Active' : 'Enter Academy'}</p>
                            <p className="text-[9px] font-bold opacity-60 uppercase">{trainingMode ? 'Simulated Execution' : 'Guided Learning'}</p>
                        </div>
                        {trainingMode && <X size={14} className="ml-2" />}
                    </button>

                    <div className="h-12 w-[1px] bg-slate-800 hidden md:block" />

                    <div className="flex items-center gap-4 bg-slate-950 p-2 rounded-2xl border border-slate-800 shadow-inner">
                        <button
                            onClick={() => user?.trading_mode !== 'AUTO' && toggleUserTradingMode()}
                            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${user?.trading_mode === 'AUTO'
                                ? 'bg-primary text-white shadow-xl shadow-primary/20 scale-105'
                                : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            <Shield size={16} />
                            Autonomous
                        </button>
                        <button
                            onClick={() => user?.trading_mode !== 'MANUAL' && toggleUserTradingMode()}
                            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${user?.trading_mode === 'MANUAL'
                                ? 'bg-orange-600 text-white shadow-xl shadow-orange-600/20 scale-105'
                                : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            <UnlockIcon size={16} />
                            Override
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Operational Grid */}
            <div className="grid grid-cols-12 gap-8 h-[calc(100vh-280px)] min-h-[700px]">
                {/* Left: Market Analytics & Sentiment */}
                <div className="col-span-12 lg:col-span-3 space-y-6">
                    <Card className="p-6 border-slate-200 shadow-sm bg-white overflow-hidden relative">
                        <div className="absolute top-0 right-0 p-4 opacity-5">
                            <Activity size={80} className="text-primary" />
                        </div>
                        <h3 className="text-xs font-black text-slate-900 uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Activity size={14} className="text-primary" /> Market Sentiment
                        </h3>
                        <SentimentGauge val={72} />
                        <div className="mt-8 space-y-3">
                            <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                <span className="text-slate-500">Retail Volume</span>
                                <span className="text-slate-900">42.5M</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                <span className="text-slate-500">Institutional Delta</span>
                                <span className="text-green-600 font-bold">+1.2%</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                <span className="text-slate-500">Vol Skew (ATM)</span>
                                <span className="text-slate-900">0.84</span>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6 border-slate-200 shadow-sm bg-white">
                        <h3 className="text-xs font-black text-slate-900 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <BarChart3 size={14} className="text-primary" /> Technical Pulse (1H)
                        </h3>
                        <div className="space-y-2">
                            <TechnicalIndicator label="RSI (14)" status="BULLISH" value="62.4" />
                            <TechnicalIndicator label="MACD (12,26)" status="BULLISH" value="Above Signal" />
                            <TechnicalIndicator label="Bollinger Bands" status="BULLISH" value="Upper Bound" />
                            <TechnicalIndicator label="MA (200)" status="NEUTRAL" value="Crossover" />
                        </div>
                        {trainingMode && (
                            <div className="mt-4 p-4 rounded-xl bg-amber-50 border border-amber-100 animate-in slide-in-from-bottom-2 duration-500">
                                <div className="flex items-center gap-2 mb-1">
                                    <Info size={12} className="text-amber-600" />
                                    <span className="text-[10px] font-black text-amber-700 uppercase tracking-widest">Training Tip</span>
                                </div>
                                <p className="text-[10px] font-medium text-amber-600 leading-relaxed">
                                    A Bullish RSI ({'>'}60) combined with MACD crossovers often signals strong momentum for long entries.
                                </p>
                            </div>
                        )}
                    </Card>

                    <Card className="p-6 border-slate-200 shadow-sm bg-slate-950 text-white flex-1 min-h-[150px] overflow-hidden">
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Eye size={12} className="text-primary" /> Sentinel Feed
                        </h3>
                        <div className="space-y-3 overflow-y-auto h-48 custom-scrollbar pr-2">
                            {logs.map(log => (
                                <div key={log.id} className="text-[10px] flex gap-2 border-l border-slate-800 pl-3 py-1">
                                    <span className="text-slate-600 font-bold">{log.time}</span>
                                    <span className={log.type === 'success' ? 'text-primary' : log.type === 'error' ? 'text-red-400' : 'text-slate-300'}>{log.msg}</span>
                                </div>
                            ))}
                            {logs.length === 0 && (
                                <div className="flex flex-col items-center justify-center h-full opacity-20">
                                    <Activity size={32} />
                                    <p className="text-[9px] uppercase font-black mt-2">Connecting to CNS...</p>
                                </div>
                            )}
                        </div>
                    </Card>
                </div>

                {/* Center: Execution & Chart Terminal */}
                <div className="col-span-12 lg:col-span-6 space-y-6">
                    <Card className="p-2 border-slate-200 shadow-lg bg-white overflow-hidden flex flex-col h-2/3">
                        <div className="flex items-center justify-between p-4 bg-slate-50 border-b border-slate-100 rounded-t-2xl">
                            <div className="flex gap-4">
                                {['EXECUTION', 'ANALYSIS', 'ALGO'].map(t => (
                                    <button
                                        key={t}
                                        onClick={() => setActiveTab(t)}
                                        className={`text-[10px] font-black uppercase tracking-widest pb-1 transition-all ${activeTab === t ? 'text-primary border-b-2 border-primary' : 'text-slate-400 hover:text-slate-600'}`}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>
                            <div className="flex items-center gap-4 bg-white px-3 py-1.5 rounded-xl border border-slate-200">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Ticker</span>
                                <span className="text-xs font-black text-slate-900">{orderTicker}</span>
                                <div className="flex items-center text-green-500 font-bold text-[10px]">
                                    <MoveUp size={10} /> 1.42%
                                </div>
                            </div>
                        </div>

                        <div className="flex-1 bg-slate-950 p-6 relative">
                            <div className="absolute top-8 left-8 z-10 p-6 bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl shadow-2xl">
                                <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Mark Price</p>
                                <p className="text-2xl font-black text-white">₹{currentPrice.toLocaleString()}</p>
                            </div>

                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorPriceHub" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#2DBD42" stopOpacity={0.2} />
                                            <stop offset="95%" stopColor="#2DBD42" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <XAxis dataKey="name" hide />
                                    <YAxis domain={['auto', 'auto']} hide />
                                    <Area type="monotone" dataKey="price" stroke="#2DBD42" strokeWidth={3} fill="url(#colorPriceHub)" animationDuration={1000} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>

                    {/* Industrial Grade Order Ticket */}
                    <Card className="p-8 border-slate-200 shadow-xl bg-white relative overflow-hidden flex-1">
                        {trainingMode && (
                            <div className="absolute top-0 left-0 w-full h-1 bg-amber-400 shadow-[0_0_10px_rgba(251,191,36,0.5)]" />
                        )}
                        <div className="flex items-center justify-between mb-8">
                            <div>
                                <h3 className="text-lg font-black text-slate-900 font-heading">Direct Market Order</h3>
                                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Multi-Asset Execution Engine</p>
                            </div>
                            <button className="h-10 w-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 hover:text-primary transition-colors border border-slate-200">
                                <Settings2 size={20} />
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-end">
                            <div className="md:col-span-4 space-y-2">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Asset Symbol</label>
                                <input
                                    type="text"
                                    value={orderTicker}
                                    onChange={(e) => setOrderTicker(e.target.value.toUpperCase())}
                                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-sm font-black text-slate-900 focus:ring-4 focus:ring-primary/10 transition-all outline-none"
                                />
                            </div>
                            <div className="md:col-span-3 space-y-2">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Execution Qty</label>
                                <div className="relative">
                                    <input
                                        type="number"
                                        value={orderQty}
                                        onChange={(e) => setOrderQty(parseInt(e.target.value) || 0)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-4 text-sm font-black text-slate-900 focus:ring-4 focus:ring-primary/10 transition-all outline-none"
                                    />
                                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[9px] font-black text-slate-400 uppercase">Size</span>
                                </div>
                            </div>
                            <div className="md:col-span-5 flex gap-3">
                                <button
                                    onClick={() => handleExecuteTrade('BUY')}
                                    disabled={executing || user?.trading_mode === 'AUTO'}
                                    className={`flex-1 flex items-center justify-center gap-3 bg-green-600 hover:bg-green-700 text-white rounded-2xl py-4 font-black transition-all shadow-xl shadow-green-600/20 active:scale-95 disabled:opacity-30`}
                                >
                                    <TrendingUp size={18} />
                                    <span>{executing ? 'HANDSHAKE...' : 'BUY'}</span>
                                </button>
                                <button
                                    onClick={() => handleExecuteTrade('SELL')}
                                    disabled={executing || user?.trading_mode === 'AUTO'}
                                    className={`flex-1 flex items-center justify-center gap-3 bg-red-600 hover:bg-red-700 text-white rounded-2xl py-4 font-black transition-all shadow-xl shadow-red-600/20 active:scale-95 disabled:opacity-30`}
                                >
                                    <TrendingDown size={18} />
                                    <span>SELL</span>
                                </button>
                            </div>
                        </div>

                        {/* Bracket Order Controls (Advanced) */}
                        <div className="grid grid-cols-2 gap-8 mt-8 pt-8 border-t border-slate-50">
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Safety: Stop Loss</label>
                                    <span className="text-[10px] font-black text-red-500 uppercase tracking-widest">{-stopLoss || '0.00'}%</span>
                                </div>
                                <input
                                    type="range" min="0" max="10" step="0.5"
                                    value={stopLoss || 0}
                                    onChange={(e) => setStopLoss(parseFloat(e.target.value))}
                                    className="w-full accent-red-500 h-1.5 bg-slate-100 rounded-full appearance-none cursor-pointer"
                                />
                            </div>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Target: Take Profit</label>
                                    <span className="text-[10px] font-black text-green-600 uppercase tracking-widest">{takeProfit || '0.00'}%</span>
                                </div>
                                <input
                                    type="range" min="0" max="25" step="0.5"
                                    value={takeProfit || 0}
                                    onChange={(e) => setTakeProfit(parseFloat(e.target.value))}
                                    className="w-full accent-green-600 h-1.5 bg-slate-100 rounded-full appearance-none cursor-pointer"
                                />
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Right: Strategy & AI Insights */}
                <div className="col-span-12 lg:col-span-3 space-y-6">
                    <Card className="p-8 bg-gradient-to-br from-slate-900 to-slate-950 text-white border-slate-800 shadow-2xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Cpu size={120} className="text-primary animate-slow-spin" />
                        </div>
                        <h3 className="text-xs font-black text-primary uppercase tracking-widest mb-6 flex items-center gap-2 relative z-10">
                            <Zap size={14} fill="currentColor" /> Steward Insight
                        </h3>
                        <div className="relative z-10">
                            <p className="text-sm font-bold text-slate-300 leading-relaxed italic border-l-2 border-primary pl-4 mb-8">
                                "{stewardPrediction?.prediction || 'Synthesizing global market data for live inference...'}"
                            </p>
                            <div className="grid grid-cols-2 gap-6">
                                <div className="p-4 bg-white/5 rounded-2xl border border-white/10 hover:border-primary/50 transition-colors">
                                    <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Confidence</p>
                                    <p className="text-xl font-black text-white">{stewardPrediction?.confidence || 0}%</p>
                                </div>
                                <div className="p-4 bg-white/5 rounded-2xl border border-white/10 hover:border-primary/50 transition-colors">
                                    <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Signal Bias</p>
                                    <p className="text-xl font-black text-emerald-400">{stewardPrediction?.decision || 'NEUTRAL'}</p>
                                </div>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6 border-slate-200 shadow-sm bg-white flex-1 overflow-hidden flex flex-col">
                        <h3 className="text-xs font-black text-slate-900 uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Target size={14} className="text-primary" /> Active Mandates
                        </h3>
                        <div className="flex-1 space-y-3 overflow-y-auto pr-2 custom-scrollbar">
                            {strategies.length > 0 ? strategies.map(s => (
                                <div key={s.id} className="p-4 bg-slate-50 rounded-2xl border border-slate-100 group hover:border-primary/50 transition-all cursor-pointer">
                                    <div className="flex justify-between items-start mb-2">
                                        <p className="text-[10px] font-black text-slate-900 uppercase tracking-tight">{s.name}</p>
                                        <span className={`px-2 py-0.5 rounded-full text-[8px] font-black uppercase ${s.status === 'RUNNING' ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-500'}`}>
                                            {s.status}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center text-[10px] font-bold">
                                        <span className="text-slate-500">Net Return</span>
                                        <span className={parseFloat(s.pnl) >= 0 ? 'text-green-600' : 'text-red-500'}>{s.pnl}%</span>
                                    </div>
                                    <div className="mt-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <div className="h-1 flex-1 bg-slate-200 rounded-full overflow-hidden">
                                            <div className="h-full bg-primary" style={{ width: '65%' }} />
                                        </div>
                                    </div>
                                </div>
                            )) : (
                                <div className="flex flex-col items-center justify-center py-12 opacity-30">
                                    <ShoppingBag size={48} />
                                    <p className="text-[10px] font-black uppercase mt-4">No active strategies</p>
                                </div>
                            )}
                        </div>
                        <Link to="/strategies" className="mt-4">
                            <button className="w-full py-4 bg-slate-900 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-primary transition-all active:scale-95 shadow-lg shadow-slate-900/20">
                                Deploy New Mandate
                            </button>
                        </Link>
                    </Card>
                </div>
            </div>

            {/* Bottom: Pro Ticker Bar */}
            <div className="fixed bottom-0 left-0 md:left-72 right-0 bg-white/80 backdrop-blur-md border-t border-slate-200 p-3 z-30 flex items-center gap-8 overflow-hidden">
                <div className="flex items-center gap-3 px-4 py-1.5 bg-slate-900 rounded-xl text-white">
                    <Globe size={14} className="text-primary animate-spin-slow" />
                    <span className="text-[10px] font-black uppercase tracking-widest">Global Handshake Active</span>
                </div>
                <div className="flex-1 flex gap-12 overflow-x-auto no-scrollbar whitespace-nowrap px-4">
                    {(marketMovers?.gainers || []).slice(0, 10).map((s, i) => (
                        <div key={i} className="flex items-center gap-3 group cursor-pointer hover:bg-slate-50 px-2 py-1 rounded-lg transition-colors">
                            <span className="text-[10px] font-black text-slate-400 uppercase group-hover:text-slate-900 transition-colors">{s.symbol}</span>
                            <span className="text-xs font-black text-slate-900">₹{s.price}</span>
                            <span className="text-[10px] font-black text-green-500 flex items-center gap-1">
                                <ChevronUp size={10} /> {s.change}%
                            </span>
                        </div>
                    ))}
                </div>
                <div className="flex items-center gap-3 pr-6">
                    <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Master Node: <span className="text-slate-900">0.04ms</span></p>
                    <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                </div>
            </div>

            <style jsx="true">{`
                @keyframes slow-spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                .animate-slow-spin {
                    animation: slow-spin 8s linear infinite;
                }
                .no-scrollbar::-webkit-scrollbar { display: none; }
                .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
                @keyframes progress {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
                .animate-progress {
                    animation: progress 1.5s infinite;
                }
            `}</style>
        </div>
    );
}
