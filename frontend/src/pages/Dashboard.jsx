import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  BarChart3, 
  Shield, 
  DollarSign, 
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Target,
  Calendar,
  Search,
  Clock,
  Settings,
  Plus,
  X,
  Play,
  Pause,
  Activity as ActivityIcon,
  Shield as ShieldIcon
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
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Link, useNavigate } from 'react-router-dom';
import { Card } from "../components/ui/card";
import { useUser } from "../context/UserContext";
import { useAppData } from "../context/AppDataContext";
import { socket, fetchPortfolioSummary, fetchTrades, fetchPortfolioHistory, fetchExchangeStatus, fetchUsers, fetchAllPortfolios, depositFunds, fetchMarketMovers } from "../services/api";

export function Dashboard() {
    const formatNumber = (value, digits = 2) => {
        const num = typeof value === 'number' ? value : parseFloat(value);
        if (!Number.isFinite(num)) return '0.00';
        return num.toFixed(digits);
    };
    const { user, selectedUser, setSelectedUser, isAdmin } = useUser();
    const {
        summary,
        trades: recentTrades,
        marketMovers: marketMoversState,
        exchangeStatus,
        stewardPrediction: stewardPredictionState,
        marketResearch,
        sectorHeatmap,
        marketNews,
        optionsSnapshot,
        orderBook,
        macroIndicators,
        adminTelemetry,
        loading,
        allUsers,
        refreshAllData
    } = useAppData();

    const [period, setPeriod] = useState('This Week');
    const [depositing, setDepositing] = useState(false);
    const [chartData, setChartData] = useState([]);
    const [socketStatus, setSocketStatus] = useState('disconnected');
    const [marketMovers, setMarketMovers] = useState({ gainers: [], losers: [] });
    const fallbackMovers = {
        gainers: [
            { symbol: 'RELIANCE', exchange: 'NSE', price: 2987.5, change: 1.2 },
            { symbol: 'HDFCBANK', exchange: 'NSE', price: 1450, change: 0.8 },
            { symbol: 'SENSEX', exchange: 'BSE', price: 72150, change: 0.6 }
        ],
        losers: [
            { symbol: 'TCS', exchange: 'NSE', price: 3450, change: -0.5 },
            { symbol: 'CRUDEOIL', exchange: 'MCX', price: 6985, change: -0.4 }
        ]
    };
    const stewardPrediction = stewardPredictionState || {
        prediction: "Initializing market intelligence...",
        decision: "HOLD",
        confidence: 0,
        signal_mix: { technical: 0, fundamental: 0, news: 0 },
        risk_radar: 0
    };

    const navigate = useNavigate();

    useEffect(() => {
        if (!socket) return;
        const up = () => setSocketStatus('connected');
        const down = () => setSocketStatus('disconnected');
        socket.on('connect', up);
        socket.on('disconnect', down);
        if (socket.connected) up();
        return () => {
            socket.off('connect', up);
            socket.off('disconnect', down);
        };
    }, []);

    // Load initial data
    useEffect(() => {
        const loadData = async () => {
            try {
                // Load portfolio summary
                const summaryData = await fetchPortfolioSummary(selectedUser?.id || user?.id);
                
                // Load recent trades
                const tradesData = await fetchTrades(selectedUser?.id || user?.id, 10);
                
                // Load market movers
                const moversData = await fetchMarketMovers();
                if (moversData?.gainers?.length || moversData?.losers?.length) {
                    setMarketMovers(moversData);
                } else {
                    setMarketMovers(fallbackMovers);
                }
                
                // Load portfolio history for chart
                const historyData = await fetchPortfolioHistory(selectedUser?.id || user?.id);
                setChartData(Array.isArray(historyData) ? historyData : [
                    { name: 'Mon', value: 100000 },
                    { name: 'Tue', value: 102000 },
                    { name: 'Wed', value: 98000 },
                    { name: 'Thu', value: 105000 },
                    { name: 'Fri', value: 107000 }
                ]);
                
                // Load exchange status
                await fetchExchangeStatus();
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                setMarketMovers(fallbackMovers);
                // Set default data if fetch fails
                setChartData([
                    { name: 'Mon', value: 100000 },
                    { name: 'Tue', value: 102000 },
                    { name: 'Wed', value: 98000 },
                    { name: 'Thu', value: 105000 },
                    { name: 'Fri', value: 107000 }
                ]);
            }
        };
        
        loadData();
    }, [selectedUser, user, isAdmin]);

    const handleQuickDeposit = async () => {
        const viewId = selectedUser?.id || user?.id;
        if (!viewId) return;
        setDepositing(true);
        try {
            const result = await depositFunds(viewId, 1000); // Quick INR 1000 deposit
            if (result) {
                await refreshAllData();
                alert("Quick Deposit of INR 1,000 successful.");
            }
        } catch (err) {
            console.error("Quick deposit failed:", err);
        } finally {
            setDepositing(false);
        }
    };

    // Define metrics with proper fallbacks
    const metrics = [
        {
            label: user?.role === 'BUSINESS_OWNER' ? 'Total Managed Assets' : 'Total Equity',
            value: `INR ${((summary?.invested_amount || 0) + (summary?.cash_balance || 0)).toLocaleString()}`,
            change: summary?.win_rate ? `+${(summary.win_rate * 0.15).toFixed(1)}%` : '+0.0%',
            icon: BarChart3,
            color: 'text-primary',
            link: '/portfolio'
        },
        {
            label: 'Ready Capital',
            value: summary ? `INR ${(summary.cash_balance || 0).toLocaleString()}` : 'INR 0',
            change: socketStatus === 'connected' ? 'SECURE' : 'OFFLINE',
            icon: DollarSign,
            color: 'text-indigo-600',
            link: '/portfolio',
            action: (
                <button
                    onClick={(e) => { 
                        e.preventDefault(); 
                        handleQuickDeposit(); 
                    }}
                    disabled={depositing}
                    className="p-1.5 hover:bg-indigo-50 rounded-lg text-indigo-400 hover:text-indigo-600 transition-colors"
                >
                    {depositing ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
                </button>
            )
        },
        {
            label: user?.role === 'AUDITOR' ? 'Audit Exposure' : 'Open Exposure',
            value: `INR ${(summary?.invested_amount || 0).toLocaleString()}`,
            change: summary?.positions_count ? `${summary.positions_count} positions` : 'No active positions',
            icon: ActivityIcon,
            color: 'text-indigo-600',
            link: '/portfolio'
        },
        {
            label: user?.role === 'BUSINESS_OWNER' ? 'Portfolio ROI' : 'Daily Alpha',
            value: `+${summary?.win_rate || 0}%`,
            change: summary?.win_rate ? `Win rate ${summary.win_rate}%` : 'Analysis pending',
            icon: TrendingUp,
            color: 'text-primary',
            link: '/reports'
        }
    ];

    if (loading) {
        return (
            <div className="h-screen flex flex-col items-center justify-center text-slate-400">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                <p className="font-black uppercase text-xs tracking-[0.3em] text-slate-500 mt-4">LOADING DASHBOARD...</p>
            </div>
        );
    }

    return (
        <div data-testid="dashboard-container" className="flex flex-col min-h-screen pb-4">
            <div className="max-w-[1600px] mx-auto space-y-8 p-6 w-full">
                <header className="flex flex-col gap-6 md:flex-row md:items-center justify-between">
                    <div>
                        <h1 className="text-2xl md:text-3xl font-black tracking-tight text-slate-900 font-heading">
                            {user?.role === 'SUPERADMIN' ? (selectedUser ? `Auditing: ${selectedUser.name || selectedUser.full_name || selectedUser.email}` : 'Platform Executive Control') :
                                user?.role === 'AUDITOR' ? 'Compliance Oversight' :
                                    user?.role === 'BUSINESS_OWNER' ? 'Executive Dashboard' :
                                        `Welcome, ${user?.name || 'Investor'}`}
                        </h1>
                        <div className="flex items-center gap-2 mt-2">
                            <span className={`h-1.5 w-1.5 rounded-full animate-pulse ${user?.role === 'SUPERADMIN' ? 'bg-indigo-500' :
                                user?.role === 'AUDITOR' ? 'bg-amber-500' :
                                    user?.role === 'BUSINESS_OWNER' ? 'bg-purple-500' :
                                        'bg-primary'
                                }`} />
                            <p className="text-slate-500 uppercase text-[10px] font-bold tracking-[0.2em] leading-none">
                                {user?.role === 'SUPERADMIN' ? (selectedUser ? 'User Inspection Mode: ACTIVE' : 'Global System Oversight: ACTIVE') :
                                    user?.role === 'AUDITOR' ? 'Audit Logging: ENABLED' :
                                        user?.role === 'BUSINESS_OWNER' ? 'Revenue Monitoring: PASSIVE' :
                                            'Personal Wealth Agent: ACTIVE'}
                            </p>
                        </div>
                    </div>
                    
                    <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
                        {isAdmin && (
                            <div className="flex items-center gap-3 bg-white border border-slate-200 p-1.5 rounded-xl shadow-sm">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-2">Scope</span>
                                <select
                                    className="bg-slate-50 border-none text-[10px] font-black uppercase tracking-widest text-slate-700 focus:ring-0 rounded-lg py-1 px-3 cursor-pointer"
                                    value={selectedUser?.id || 'GLOBAL'}
                                    onChange={(e) => {
                                        const val = e.target.value;
                                        if (val === 'GLOBAL') {
                                            setSelectedUser(null);
                                        } else {
                                            const u = allUsers.find(user => user.id === parseInt(val));
                                            if (u) {
                                                setSelectedUser({
                                                    ...u,
                                                    name: u.full_name || u.name || u.email
                                                });
                                            }
                                        }
                                    }}
                                >
                                    <option value="GLOBAL">Platform Summary</option>
                                    <optgroup label="Active Users">
                                        {allUsers.map(u => (
                                            <option key={u.id} value={u.id}>{u.full_name || u.name || u.email}</option>
                                        ))}
                                    </optgroup>
                                </select>
                            </div>
                        )}
                        <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 w-full md:w-auto overflow-x-auto">
                            {['Today', 'This Week', 'This Year'].map((p) => (
                                <button
                                    key={p}
                                    onClick={() => setPeriod(p)}
                                    className={`flex-1 md:flex-none px-4 py-2 text-xs font-black rounded-lg transition-all whitespace-nowrap ${period === p ? 'bg-white shadow-md text-primary' : 'text-slate-400 hover:text-slate-700'
                                        }`}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>
                    </div>
                </header>

                {/* AI Intelligence Card */}
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                        <ShieldIcon size={160} className="text-primary rotate-12" />
                    </div>

                    <div className="relative z-10 space-y-8">
                        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                            <div className="flex items-center gap-4">
                                <div className="h-14 w-14 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30 shrink-0">
                                    <Zap className="text-primary animate-pulse" size={28} />
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-[10px] font-black text-primary uppercase tracking-[0.3em]">GUARDIAN INTELLIGENCE</span>
                                        <span className="h-1 w-1 rounded-full bg-slate-700" />
                                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">REAL-TIME ANALYSIS</span>
                                    </div>
                                    <h2 className="text-white text-xl font-black tracking-tight leading-tight max-w-2xl">
                                        {stewardPrediction?.prediction || "Synchronizing with market sentiment..."}
                                    </h2>
                                </div>
                            </div>

                            <div className="flex gap-4 w-full md:w-auto">
                                <Link to="/trading" className="flex-1 md:flex-none">
                                    <button className="w-full bg-primary hover:bg-primary/90 text-white px-6 py-3.5 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all hover:scale-105 active:scale-95 shadow-lg shadow-primary/20 flex items-center justify-center gap-2">
                                        <ActivityIcon size={14} />
                                        LAUNCH STRATEGY
                                    </button>
                                </Link>
                                <button className="flex-1 md:flex-none bg-slate-800 hover:bg-slate-700 text-slate-300 px-6 py-3.5 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all border border-slate-700">
                                    VIEW LOGIC
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-6 border-t border-slate-800/50">
                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">AI DECISION</p>
                                <div className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest ${
                                    stewardPrediction?.decision?.includes('BUY') ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                    stewardPrediction?.decision?.includes('SELL') ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                                    'bg-slate-700/50 text-slate-400 border border-slate-600/30'
                                }`}>
                                    {stewardPrediction?.decision || "HOLD"}
                                </div>
                                <span className="text-[10px] font-bold text-slate-500">MEDIUM TERM</span>
                            </div>

                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">MODEL CONFIDENCE</p>
                                <div className="flex items-center gap-3">
                                    <span className="text-xl font-black text-white">{stewardPrediction?.confidence || 0}%</span>
                                    <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary transition-all duration-1000"
                                            style={{ width: `${stewardPrediction?.confidence || 0}%` }}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">SIGNAL MIX</p>
                                <div className="flex flex-wrap gap-2">
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">TECH: {stewardPrediction?.signal_mix?.technical || 0}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">FUND: {stewardPrediction?.signal_mix?.fundamental || 0}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-orange-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">NEWS: {stewardPrediction?.signal_mix?.news || 0}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2 border-l border-slate-800/50 pl-6">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">RISK RADAR</p>
                                <div className="flex items-center gap-3">
                                    <div className="relative h-10 w-10 flex items-center justify-center">
                                        <svg className="h-10 w-10 -rotate-90">
                                            <circle cx="20" cy="20" r="18" fill="transparent" stroke="currentColor" strokeWidth="3" className="text-slate-800" />
                                            <circle 
                                                cx="20" 
                                                cy="20" 
                                                r="18" 
                                                fill="transparent" 
                                                stroke="currentColor" 
                                                strokeWidth="3" 
                                                strokeDasharray={113} 
                                                strokeDashoffset={113 - (113 * (stewardPrediction?.risk_radar || 0)) / 100} 
                                                className="text-red-500 transition-all duration-1000"
                                            />
                                        </svg>
                                        <span className="absolute text-[8px] font-black text-white">{stewardPrediction?.risk_radar || 0}</span>
                                    </div>
                                    <div>
                                        <p className="text-[10px] font-black text-white leading-none">HIGH VOLATILITY</p>
                                        <p className="text-[8px] font-bold text-slate-500 uppercase mt-1">NIFTY EXPOSURE</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Metrics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {metrics.map((metric, i) => (
                        <Link to={metric.link} key={i}>
                            <Card className="p-6 border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group bg-white h-full cursor-pointer">
                                <div className="flex justify-between items-start mb-4">
                                    <div className={`p-2.5 rounded-xl bg-slate-50 transition-colors group-hover:bg-primary/5 ${metric.color}`}>
                                        <metric.icon size={18} />
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {metric.action}
                                        <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                                            metric.change.startsWith('+') || metric.change.includes('SECURE') 
                                                ? 'bg-green-50 text-green-700' 
                                                : 'bg-slate-100 text-slate-600'
                                        }`}>
                                            {metric.change}
                                        </span>
                                    </div>
                                </div>
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">{metric.label}</p>
                                <h3 className="text-2xl font-black text-slate-900 tracking-tight">{metric.value}</h3>
                            </Card>
                        </Link>
                    ))}
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
                    {/* Portfolio Performance Chart */}
                    <Card className="xl:col-span-8 p-8 border-slate-100 shadow-sm bg-white overflow-hidden relative">
                        <div className="flex items-center justify-between mb-8">
                            <div>
                                <h2 className="text-lg font-black text-slate-900 font-heading">
                                    {user?.role === 'AUDITOR' ? 'Compliance Alpha Curve' : 'Performance Alpha'}
                                </h2>
                                <p className="text-xs text-slate-500 font-medium">
                                    {user?.role === 'AUDITOR' ? 'System execution integrity audit' : 'Net performance curve across all active strategies'}
                                </p>
                            </div>
                            <div className="flex gap-2">
                                <div className="h-3 w-3 rounded-full bg-primary" />
                                <span className="text-[10px] font-black text-slate-400 uppercase">Steward Equity</span>
                            </div>
                        </div>
                        <div className="h-[350px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                    <XAxis
                                        dataKey="name"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fontSize: 11, fill: '#94a3b8', fontWeight: 600 }}
                                    />
                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fontSize: 11, fill: '#94a3b8', fontWeight: 600 }}
                                        tickFormatter={(val) => `INR ${val}`}
                                    />
                                    <Tooltip
                                        formatter={(value) => [`INR ${value}`, 'Value']}
                                        labelFormatter={(label) => `Date: ${label}`}
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
                                        stroke="#3b82f6"
                                        strokeWidth={4}
                                        fillOpacity={1}
                                        fill="url(#colorValue)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>

                    {/* AI Analyst and Top Movers */}
                    <div className="xl:col-span-4 space-y-6">
                        <Card className="p-6 border-slate-100 shadow-sm bg-white">
                            <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">AI Analyst Insights</h3>
                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                                    <p className="text-xs text-slate-700 leading-relaxed">
                                        {stewardPrediction?.prediction || "AI is analyzing market conditions and generating insights..."}
                                    </p>
                                </div>
                                <div className="flex justify-between text-xs">
                                    <span className="text-slate-500">Market Sentiment</span>
                                    <span className="font-black text-primary">BULLISH</span>
                                </div>
                                <div className="flex justify-between text-xs">
                                    <span className="text-slate-500">Volatility Level</span>
                                    <span className="font-black text-amber-500">MODERATE</span>
                                </div>
                            </div>
                        </Card>

                        <Card className="p-6 border-slate-100 shadow-sm bg-white">
                            <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Top Movers</h3>
                            <div className="space-y-3">
                                {(marketMovers?.gainers?.length ? marketMovers.gainers : fallbackMovers.gainers).slice(0, 3).map((mover, i) => (
                                    <div key={i} className="flex justify-between items-center">
                                        <div>
                                            <p className="font-black text-slate-900">{mover.symbol}</p>
                                            <p className="text-[10px] text-slate-500">+{mover.change}%</p>
                                        </div>
                                        <p className="font-black text-green-600">INR {formatNumber(mover.price, 2)}</p>
                                    </div>
                                ))}
                                {(marketMovers?.losers?.length ? marketMovers.losers : fallbackMovers.losers).slice(0, 2).map((mover, i) => (
                                    <div key={i} className="flex justify-between items-center">
                                        <div>
                                            <p className="font-black text-slate-900">{mover.symbol}</p>
                                            <p className="text-[10px] text-slate-500">{mover.change}%</p>
                                        </div>
                                        <p className="font-black text-red-500">INR {formatNumber(mover.price, 2)}</p>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Market Intelligence */}
                    <Card className="p-6 border-slate-100 shadow-sm bg-white">
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Market Intelligence</h3>
                        <div className="space-y-3">
                            {(marketResearch?.headlines || []).slice(0, 5).map((headline, i) => (
                                <div key={i} className="p-3 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between">
                                    <span className="text-xs font-bold text-slate-800">{headline}</span>
                                    <span className="text-[9px] font-black text-primary uppercase">Insight</span>
                                </div>
                            ))}
                            {(!marketResearch || !marketResearch.headlines || marketResearch.headlines.length === 0) && (
                                <div className="text-xs text-slate-400 italic text-center py-4">No market intelligence available</div>
                            )}
                        </div>
                    </Card>

                    {/* Order Book Depth */}
                    <Card className="p-6 border-slate-100 shadow-sm bg-white">
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Order Book Depth</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Bids</p>
                                {(orderBook?.bids || []).slice(0, 5).map((bid, i) => (
                                    <div key={i} className="flex justify-between text-xs font-bold text-slate-700 py-1">
                                        <span>INR {formatNumber(bid.price, 2)}</span>
                                        <span>{bid.qty}</span>
                                    </div>
                                ))}
                                {(!orderBook || !orderBook.bids || orderBook.bids.length === 0) && (
                                    <div className="text-xs text-slate-400 italic">No bid data available</div>
                                )}
                            </div>
                            <div>
                                <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Asks</p>
                                {(orderBook?.asks || []).slice(0, 5).map((ask, i) => (
                                    <div key={i} className="flex justify-between text-xs font-bold text-slate-700 py-1">
                                        <span>INR {formatNumber(ask.price, 2)}</span>
                                        <span>{ask.qty}</span>
                                    </div>
                                ))}
                                {(!orderBook || !orderBook.asks || orderBook.asks.length === 0) && (
                                    <div className="text-xs text-slate-400 italic">No ask data available</div>
                                )}
                            </div>
                        </div>
                    </Card>

                    {/* Exchange Status */}
                    <Card className="p-6 border-slate-100 shadow-sm bg-white">
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Exchange Status</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-slate-600">NSE</span>
                                <span className={`text-xs font-black px-2 py-0.5 rounded-full ${
                                    exchangeStatus?.nse === 'open' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                }`}>
                                    {exchangeStatus?.nse || 'closed'}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-600">BSE</span>
                                <span className={`text-xs font-black px-2 py-0.5 rounded-full ${
                                    exchangeStatus?.bse === 'open' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                }`}>
                                    {exchangeStatus?.bse || 'closed'}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-600">MCX</span>
                                <span className={`text-xs font-black px-2 py-0.5 rounded-full ${
                                    exchangeStatus?.mcx === 'open' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                }`}>
                                    {exchangeStatus?.mcx || 'closed'}
                                </span>
                            </div>
                            <div className="pt-2 border-t border-slate-100">
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-600">System Status</span>
                                    <span className={`text-xs font-black px-2 py-0.5 rounded-full ${
                                        socketStatus === 'connected' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                                    }`}>
                                        {socketStatus}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Recent Trades */}
                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Recent Trades</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-slate-100">
                                    <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">Symbol</th>
                                    <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">Side</th>
                                    <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">Quantity</th>
                                    <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">Price</th>
                                    <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">PnL</th>
                                    <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(recentTrades || []).slice(0, 5).map((trade, i) => (
                                    <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                                        <td className="py-3 font-black text-slate-900">{trade.symbol}</td>
                                        <td className={`py-3 font-black ${trade.side === 'BUY' ? 'text-green-600' : 'text-red-500'}`}>
                                            {trade.side}
                                        </td>
                                        <td className="py-3 text-slate-700">{trade.quantity}</td>
                                        <td className="py-3 font-black text-slate-900">INR {formatNumber(trade.entry_price, 2)}</td>
                                        <td className={`py-3 font-black ${trade.pnl > 0 ? 'text-green-600' : 'text-red-500'}`}>
                                            {trade.pnl > 0 ? '+' : ''}{formatNumber(trade.pnl, 2)}
                                        </td>
                                        <td className="py-3 text-[10px] text-slate-500">
                                            {new Date(trade.timestamp || trade.created_at).toLocaleTimeString()}
                                        </td>
                                    </tr>
                                ))}
                                {(!recentTrades || recentTrades.length === 0) && (
                                    <tr>
                                        <td colSpan="6" className="py-8 text-center text-slate-400 text-sm">No recent trades</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </Card>
            </div>
        </div>
    );
}

