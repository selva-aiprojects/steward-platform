import React, { useState, useEffect, useMemo } from 'react';
import { Card } from "../components/ui/card";
import {
    Zap,
    Target,
    Activity,
    TrendingUp,
    TrendingDown,
    ArrowUpRight,
    ArrowDownRight,
    Shield,
    Loader2,
    Settings2,
    X,
    Maximize2,
    BarChart3,
    History,
    LayoutGrid,
    Search,
    ChevronRight,
    ChevronDown,
    Circle,
    Info,
    AlertCircle,
    ShoppingBag,
    Database,
    Lock,
    Unlock,
    Flame
} from 'lucide-react';
import {
    LineChart,
    Line,
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
    useAppData
} from "../context/AppDataContext";
import {
    useUser
} from "../context/UserContext";
import {
    executeTrade,
    fetchHoldings,
    launchStrategy
} from "../services/api";

// --- Mock Components for the Pro Feel ---

const OrderBook = ({ price }) => {
    const asks = useMemo(() => Array.from({ length: 8 }, (_, i) => ({
        price: (price + (8 - i) * 0.25).toFixed(2),
        size: Math.floor(Math.random() * 500) + 10,
        total: Math.floor(Math.random() * 2000) + 500
    })), [price]);

    const bids = useMemo(() => Array.from({ length: 8 }, (_, i) => ({
        price: (price - (i + 1) * 0.25).toFixed(2),
        size: Math.floor(Math.random() * 500) + 10,
        total: Math.floor(Math.random() * 2000) + 500
    })), [price]);

    return (
        <div className="flex flex-col h-full bg-slate-900/50 rounded-xl overflow-hidden border border-slate-800">
            <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900">
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Order Book</span>
                <div className="flex gap-1">
                    <Circle size={8} className="text-red-500 fill-red-500" />
                    <Circle size={8} className="text-green-500 fill-green-500" />
                </div>
            </div>

            <div className="flex-1 overflow-hidden flex flex-col">
                {/* Asks */}
                <div className="flex-1 overflow-y-auto px-1">
                    {asks.map((ask, i) => (
                        <div key={`ask-${i}`} className="grid grid-cols-3 py-1 text-[10px] font-medium hover:bg-red-500/5 transition-colors relative">
                            <div className="absolute right-0 top-0 bottom-0 bg-red-500/10" style={{ width: `${(ask.size / 510) * 100}%` }} />
                            <span className="text-red-400 z-10 pl-2">{ask.price}</span>
                            <span className="text-slate-300 text-right z-10">{ask.size}</span>
                            <span className="text-slate-500 text-right pr-2 z-10">{ask.total}</span>
                        </div>
                    ))}
                </div>

                {/* Spread */}
                <div className="py-2 bg-slate-900 border-y border-slate-800 flex justify-center items-center gap-4">
                    <span className="text-xs font-black text-white">{price}</span>
                    <span className="text-[10px] text-slate-500 font-bold">SPREAD: 0.25 (0.01%)</span>
                </div>

                {/* Bids */}
                <div className="flex-1 overflow-y-auto px-1">
                    {bids.map((bid, i) => (
                        <div key={`bid-${i}`} className="grid grid-cols-3 py-1 text-[10px] font-medium hover:bg-green-500/5 transition-colors relative">
                            <div className="absolute right-0 top-0 bottom-0 bg-green-500/10" style={{ width: `${(bid.size / 510) * 100}%` }} />
                            <span className="text-green-400 z-10 pl-2">{bid.price}</span>
                            <span className="text-slate-300 text-right z-10">{bid.size}</span>
                            <span className="text-slate-500 text-right pr-2 z-10">{bid.total}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

const MiniChart = ({ color = "#3b82f6", label, value, change }) => {
    const data = useMemo(() => Array.from({ length: 15 }, (_, i) => ({ v: Math.random() * 20 + 40 })), []);
    return (
        <div className="bg-slate-900/40 p-3 rounded-xl border border-slate-800 flex items-center gap-4">
            <div className="flex-1">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{label}</p>
                <p className="text-sm font-black text-white mt-0.5">{value}</p>
                <p className={`text-[10px] font-bold mt-0.5 ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {change >= 0 ? '+' : ''}{change}%
                </p>
            </div>
            <div className="w-16 h-10 min-h-[40px]">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <Area type="monotone" dataKey="v" stroke={color} fill={color} fillOpacity={0.1} strokeWidth={2} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

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

// --- Main Page Component ---

export default function TradingPlatform() {
    const { user } = useUser();
    const {
        summary,
        marketMovers,
        strategies: appStrategies,
        refreshAllData,
        toggleTradingMode: toggleUserTradingMode,
        loading
    } = useAppData();

    const [activeSymbol, setActiveSymbol] = useState('RELIANCE');
    const [assetClass, setAssetClass] = useState('EQUITY');
    const [orderSide, setOrderSide] = useState('BUY');
    const [orderQty, setOrderQty] = useState(10);
    const [orderType, setOrderType] = useState('MARKET');
    const [executing, setExecuting] = useState(false);
    const [activeTab, setActiveTab] = useState('CHART'); // CHART, ORDER_HISTORY, STRATEGIES
    const [activeHoldings, setActiveHoldings] = useState([]);
    const [logs, setLogs] = useState([]);
    const [showConfirmation, setShowConfirmation] = useState(false);

    // Live price simulation
    const currentPrice = useMemo(() => {
        if (!marketMovers) return 2450.00;
        const all = [...(marketMovers.gainers || []), ...(marketMovers.losers || [])];
        const found = all.find(m => m.symbol === activeSymbol);
        return found ? found.price : 2450.00;
    }, [activeSymbol, marketMovers]);

    const chartData = useMemo(() => {
        return Array.from({ length: 40 }, (_, i) => ({
            time: `${10 + Math.floor(i / 4)}:${(i % 4) * 15}`,
            price: currentPrice + (Math.random() - 0.5) * 50,
            volume: Math.floor(Math.random() * 1000) + 200
        }));
    }, [currentPrice, activeSymbol]);

    useEffect(() => {
        const loadHoldings = async () => {
            if (user) {
                const h = await fetchHoldings(user.id);
                setActiveHoldings(h || []);
            }
        };
        loadHoldings();
    }, [user]);

    const handleExecuteTrade = async () => {
        if (!user || orderQty <= 0) return;

        // Show the institutional handshake first
        setShowConfirmation(true);
    };

    const onHandshakeComplete = async () => {
        setShowConfirmation(false);
        setExecuting(true);
        try {
            const data = {
                symbol: activeSymbol,
                side: orderSide,
                quantity: orderQty,
                price: currentPrice,
                order_type: orderType,
                asset_class: assetClass,
                decision_logic: `Pro Platform Manual Execution: ${orderSide} ${orderQty} ${activeSymbol} @ MARKET`
            };
            await executeTrade(user.id, data);
            await refreshAllData();
            const h = await fetchHoldings(user.id);
            setActiveHoldings(h || []);
            setLogs(prev => [{
                id: Date.now(),
                msg: `Order Executed: ${orderSide} ${orderQty} units of ${activeSymbol}`,
                type: 'success',
                time: new Date().toLocaleTimeString()
            }, ...prev]);
        } catch (err) {
            setLogs(prev => [{
                id: Date.now(),
                msg: `Execution Error: ${err.message}`,
                type: 'error',
                time: new Date().toLocaleTimeString()
            }, ...prev]);
        } finally {
            setExecuting(false);
        }
    };

    if (loading) {
        return (
            <div className="h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-500 overflow-hidden">
                <Loader2 className="animate-spin text-primary mb-6" size={48} />
                <p className="text-xs font-black uppercase tracking-[0.4em] animate-pulse">Initializing Trading Core...</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-300 p-2 md:p-4 flex flex-col gap-4 font-sans select-none overflow-hidden max-h-screen">
            <ConfirmationOverlay show={showConfirmation} onComplete={onHandshakeComplete} />
            {/* Top Bar: Live Stats */}
            <div className="flex flex-wrap items-center gap-4 bg-slate-900/80 border border-slate-800 p-3 rounded-2xl backdrop-blur-md">
                <div className="flex items-center gap-3 pr-4 border-r border-slate-800">
                    <div className="h-10 w-10 bg-primary/20 rounded-xl flex items-center justify-center text-primary border border-primary/20 shadow-lg shadow-primary/10">
                        <Flame size={20} fill="currentColor" />
                    </div>
                    <div>
                        <h2 className="text-sm font-black text-white tracking-tight uppercase">{activeSymbol}</h2>
                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none">NSE · INDIA</span>
                    </div>
                </div>

                <div className="flex gap-8 px-4 flex-1 overflow-x-auto no-scrollbar">
                    <div className="flex flex-col">
                        <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Last Price</span>
                        <div className="flex items-center gap-2">
                            <span className="text-xl font-black text-white">₹{currentPrice.toLocaleString()}</span>
                            <div className="flex items-center text-green-400 text-[10px] font-bold">
                                <ArrowUpRight size={12} />
                                1.25%
                            </div>
                        </div>
                    </div>

                    <div className="hidden lg:flex flex-col">
                        <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">24h High</span>
                        <span className="text-sm font-bold text-slate-200">₹{(currentPrice + 45).toLocaleString()}</span>
                    </div>

                    <div className="hidden lg:flex flex-col">
                        <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">24h Low</span>
                        <span className="text-sm font-bold text-slate-200">₹{(currentPrice - 20).toLocaleString()}</span>
                    </div>

                    <div className="hidden xl:flex flex-col">
                        <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Volume (24h)</span>
                        <span className="text-sm font-bold text-slate-200">4.82M</span>
                    </div>

                    <div className="flex flex-col">
                        <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Ready Capital</span>
                        <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-primary">₹{summary?.cash_balance?.toLocaleString() || '0'}</span>
                            <button
                                onClick={() => window.location.href = '/portfolio'}
                                className="px-2 py-0.5 bg-primary/10 text-primary text-[8px] font-black rounded border border-primary/20 hover:bg-primary/20 transition-all"
                            >
                                TOP UP
                            </button>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
                    <button
                        onClick={toggleUserTradingMode}
                        className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${user?.trading_mode === 'AUTO'
                            ? 'bg-primary/20 text-primary border border-primary/20 shadow-lg shadow-primary/5'
                            : 'bg-orange-500/10 text-orange-500 border border-orange-500/20 shadow-lg shadow-orange-500/5'}`}
                    >
                        {user?.trading_mode === 'AUTO' ? <Shield size={14} className="animate-pulse" /> : <Unlock size={14} />}
                        {user?.trading_mode === 'AUTO' ? 'STEWARD ACTIVE' : 'MANUAL OVERRIDE'}
                    </button>
                    <button className="p-2.5 bg-slate-800 text-slate-400 rounded-xl hover:text-white transition-colors border border-slate-700">
                        <Settings2 size={18} />
                    </button>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
                {/* Left Column: Watchlist / Market */}
                <div className="hidden lg:flex col-span-2 flex-col gap-4">
                    <Card className="flex-1 bg-slate-900 border-slate-800 flex flex-col p-4 overflow-hidden">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-xs font-black text-white uppercase tracking-widest">Watchlist</h3>
                            <Search size={14} className="text-slate-500" />
                        </div>
                        <div className="flex-1 overflow-y-auto pr-2 space-y-1 custom-scrollbar">
                            {(marketMovers?.gainers || []).concat(marketMovers?.losers || []).slice(0, 15).map((stock, i) => (
                                <button
                                    key={i}
                                    onClick={() => setActiveSymbol(stock.symbol)}
                                    className={`w-full flex items-center justify-between p-2.5 rounded-xl transition-all group ${activeSymbol === stock.symbol ? 'bg-primary shadow-lg shadow-primary/20 text-white' : 'hover:bg-slate-800 text-slate-400'}`}
                                >
                                    <div className="text-left">
                                        <div className="text-[10px] font-black uppercase">{stock.symbol}</div>
                                        <div className="text-[8px] font-bold opacity-60 uppercase">NSE</div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-[10px] font-black ${activeSymbol === stock.symbol ? 'text-white' : (stock.change >= 0 ? 'text-green-400' : 'text-red-400')}`}>
                                            ₹{stock.price}
                                        </div>
                                        <div className="text-[8px] font-bold opacity-60 flex items-center justify-end">
                                            {stock.change >= 0 ? <ArrowUpRight size={8} /> : <ArrowDownRight size={8} />}
                                            {stock.change}%
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </Card>
                </div>

                {/* Central Column: Chart & Workspace */}
                <div className="col-span-12 lg:col-span-7 flex flex-col gap-4">
                    <Card className="flex-1 bg-slate-900 border-slate-800 flex flex-col overflow-hidden">
                        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
                            <div className="flex gap-4">
                                {['CHART', 'DEPTH', 'TRADES'].map(t => (
                                    <button
                                        key={t}
                                        onClick={() => setActiveTab(t)}
                                        className={`text-[10px] font-black uppercase tracking-widest pb-1 transition-all ${activeTab === t ? 'text-primary border-b-2 border-primary' : 'text-slate-500 hover:text-slate-300'}`}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="flex bg-slate-800 p-0.5 rounded-lg border border-slate-700">
                                    {['1m', '5m', '15m', '1h', '1d'].map(tf => (
                                        <button key={tf} className="px-2 py-1 text-[8px] font-black text-slate-400 hover:text-white hover:bg-slate-700 rounded-md transition-all uppercase">{tf}</button>
                                    ))}
                                </div>
                                <Maximize2 size={16} className="text-slate-500 hover:text-white cursor-pointer" />
                            </div>
                        </div>

                        <div className="flex-1 flex flex-col bg-slate-950 p-4 relative min-h-[400px]">
                            <div className="absolute top-8 left-8 z-10 p-4 bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl">
                                <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Live Feed</h4>
                                <p className="text-xl font-black text-white">₹{currentPrice.toLocaleString()}</p>
                            </div>

                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                    <XAxis
                                        dataKey="time"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#475569', fontSize: 10 }}
                                        minTickGap={30}
                                    />
                                    <YAxis
                                        domain={['auto', 'auto']}
                                        orientation="right"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#475569', fontSize: 10 }}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }}
                                        itemStyle={{ color: '#fff', fontSize: '12px' }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="price"
                                        stroke="#3b82f6"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorPrice)"
                                        animationDuration={1000}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>

                    {/* Bottom Panel: Activity & Logs */}
                    <div className="h-48 grid grid-cols-2 gap-4">
                        <Card className="bg-slate-900 border-slate-800 p-4 overflow-hidden flex flex-col">
                            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                                <History size={12} /> Execution Logs
                            </h3>
                            <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                                {logs.length > 0 ? logs.map(log => (
                                    <div key={log.id} className="text-[10px] flex gap-3 p-2 bg-slate-950/50 rounded-lg border border-slate-800/50">
                                        <span className="text-slate-600 font-bold">{log.time}</span>
                                        <span className={log.type === 'success' ? 'text-green-400' : 'text-red-400'}>{log.msg}</span>
                                    </div>
                                )) : (
                                    <div className="h-full flex flex-col items-center justify-center opacity-30">
                                        <Database size={24} className="mb-2" />
                                        <p className="text-[10px] uppercase font-black">No signals processed</p>
                                    </div>
                                )}
                            </div>
                        </Card>
                        <Card className="bg-slate-900 border-slate-800 p-4">
                            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                                <Activity size={12} /> Live Metrics
                            </h3>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800/50">
                                    <p className="text-[8px] font-black text-slate-500 uppercase mb-1">Execution Speed</p>
                                    <p className="text-sm font-black text-white">42ms</p>
                                </div>
                                <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800/50">
                                    <p className="text-[8px] font-black text-slate-500 uppercase mb-1">Signal Confidence</p>
                                    <p className="text-sm font-black text-emerald-400">84%</p>
                                </div>
                                <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800/50">
                                    <p className="text-[8px] font-black text-slate-500 uppercase mb-1">Spread Impact</p>
                                    <p className="text-sm font-black text-white">0.02%</p>
                                </div>
                                <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800/50">
                                    <p className="text-[8px] font-black text-slate-500 uppercase mb-1">API Status</p>
                                    <div className="flex items-center gap-1">
                                        <Circle size={8} className="fill-green-500 text-green-500 animate-pulse" />
                                        <span className="text-xs font-black text-white">NOMINAL</span>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>

                {/* Right Column: Order Entry & Depth */}
                <div className="col-span-12 lg:col-span-3 flex flex-col gap-4">
                    {/* Order Entry */}
                    <Card className="bg-slate-900 border-slate-800 p-5 flex flex-col overflow-hidden shadow-2xl">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xs font-black text-white uppercase tracking-widest">Master Execution</h3>
                            <button className="text-slate-500 hover:text-white transition-colors">
                                <Settings2 size={16} />
                            </button>
                        </div>

                        <div className="flex gap-2 p-1 bg-slate-950 rounded-2xl border border-slate-800 mb-6">
                            {['BUY', 'SELL'].map(s => (
                                <button
                                    key={s}
                                    onClick={() => setOrderSide(s)}
                                    className={`flex-1 py-3 rounded-xl text-xs font-black tracking-widest transition-all ${orderSide === s
                                        ? (s === 'BUY' ? 'bg-green-600 shadow-lg shadow-green-900/40 text-white' : 'bg-red-600 shadow-lg shadow-red-900/40 text-white')
                                        : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>

                        <div className="space-y-5">
                            <div className="space-y-2">
                                <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest ml-1">Order Type</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {['MARKET', 'LIMIT'].map(t => (
                                        <button
                                            key={t}
                                            onClick={() => setOrderType(t)}
                                            className={`py-2.5 rounded-xl text-[10px] font-black tracking-widest border transition-all ${orderType === t ? 'bg-slate-800 border-primary text-white' : 'bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700'}`}
                                        >
                                            {t}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest ml-1">Asset Class</label>
                                <select
                                    value={assetClass}
                                    onChange={(e) => setAssetClass(e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-xs font-bold text-white outline-none focus:border-primary transition-all"
                                >
                                    <option value="EQUITY">EQUITY</option>
                                    <option value="OPTIONS">DERIVATIVES</option>
                                    <option value="COMMODITIES">COMMODITIES</option>
                                    <option value="CURRENCY">FOREX</option>
                                </select>
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-between items-center ml-1">
                                    <label className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Quantity</label>
                                    <span className="text-[8px] font-black text-primary uppercase">MAX: 4200</span>
                                </div>
                                <div className="relative">
                                    <input
                                        type="number"
                                        value={orderQty}
                                        onChange={(e) => setOrderQty(parseInt(e.target.value) || 0)}
                                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm font-black text-white outline-none focus:border-primary transition-all pr-12"
                                    />
                                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] font-black text-slate-600">LOTS</span>
                                </div>
                            </div>

                            <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 space-y-2">
                                <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
                                    <span className="text-slate-500">Margin Req</span>
                                    <span className="text-white">₹{(currentPrice * orderQty * 0.1).toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
                                    <span className="text-slate-500">Est. Total</span>
                                    <span className="text-white">₹{(currentPrice * orderQty).toFixed(2)}</span>
                                </div>
                            </div>

                            <button
                                onClick={handleExecuteTrade}
                                disabled={executing || !user}
                                className={`w-full py-5 rounded-2xl font-black text-xs uppercase tracking-[0.3em] transition-all shadow-2xl active:scale-95 flex items-center justify-center gap-3 ${orderSide === 'BUY'
                                    ? 'bg-green-600 hover:bg-green-500 text-white shadow-green-900/30'
                                    : 'bg-red-600 hover:bg-red-500 text-white shadow-red-900/30'}`}
                            >
                                {executing ? <Loader2 className="animate-spin" size={18} /> : (orderSide === 'BUY' ? <TrendingUp size={18} /> : <TrendingDown size={18} />)}
                                PROMPT {orderSide}
                            </button>
                        </div>
                    </Card>

                    {/* Order Book Depth Mock */}
                    <div className="flex-1 min-h-0">
                        <OrderBook price={currentPrice} />
                    </div>
                </div>
            </div>

            {/* Bottom Row: Quick Stats Carousel / Active Positions */}
            <div className="h-24 flex gap-4">
                <div className="flex-1 flex gap-4 overflow-x-auto no-scrollbar">
                    <MiniChart label="VIX Index" value="14.82" change={-2.4} color="#facc15" />
                    <MiniChart label="NIFTY 50" value="22,451.20" change={0.84} color="#10b981" />
                    <MiniChart label="Active Delta" value="0.92" change={1.2} color="#3b82f6" />
                    <MiniChart label="Theta Decay" value="-42.50" change={-5.2} color="#f87171" />
                    <div className="hidden 2xl:flex bg-slate-900/40 p-3 rounded-xl border border-slate-800 flex-col justify-center min-w-[200px]">
                        <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Active Mandates</p>
                        <div className="flex items-center gap-2 mt-1">
                            {appStrategies?.slice(0, 3).map((s, i) => (
                                <div key={i} className="h-6 w-6 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/20" title={s.name}>
                                    <Zap size={12} className="text-primary" />
                                </div>
                            ))}
                            <span className="text-xs font-black text-white ml-1">+{appStrategies?.length > 3 ? appStrategies.length - 3 : 0} Running</span>
                        </div>
                    </div>
                </div>

                <div className="w-[300px] bg-slate-900 border border-slate-800 rounded-xl p-3 flex items-center justify-between">
                    <div>
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Active P/L</p>
                        <p className="text-lg font-black text-green-400">+₹4,821.50</p>
                    </div>
                    <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-[10px] font-black uppercase text-white transition-all border border-slate-700">
                        EXIT ALL
                    </button>
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
                @keyframes progress {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
                .animate-progress {
                    animation: progress 1.5s infinite;
                }
                .no-scrollbar::-webkit-scrollbar { display: none; }
                .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
            `}</style>
        </div>
    );
}
