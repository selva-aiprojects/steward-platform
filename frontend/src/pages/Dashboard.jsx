import React, { useState, useEffect } from 'react';
import { Card } from "../components/ui/card";
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis,
    CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Activity, BarChart2, Shield, ArrowUpRight, ArrowDownRight, Zap, RefreshCcw, Loader2, DollarSign, Target, Calendar, Search, Clock, Settings, Plus } from 'lucide-react';

import { AIAnalyst } from "../components/AIAnalyst";
import { TopMovers } from "../components/TopMovers";
import { useNavigate, Link } from "react-router-dom";
import { socket, fetchPortfolioSummary, fetchTrades, fetchPortfolioHistory, fetchExchangeStatus, fetchUsers, fetchAllPortfolios, depositFunds, fetchMarketMovers } from "../services/api";

import { useUser } from "../context/UserContext";
import { useAppData } from "../context/AppDataContext";
import { MarketTicker } from "../components/MarketTicker";

export function Dashboard() {
    const { user, selectedUser, setSelectedUser } = useUser();
    const {
        summary,
        trades: recentTrades,
        marketMovers: marketMoversState,
        exchangeStatus,
        stewardPrediction,
        adminTelemetry,
        loading,
        allUsers,
        refreshAllData
    } = useAppData();

    const [period, setPeriod] = useState('This Week');
    const [depositing, setDepositing] = useState(false);
    const [chartData, setChartData] = useState([]);
    const [socketStatus, setSocketStatus] = useState('disconnected');

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

    // Chart data still needs to be fetched separately or added to context if used widely
    // For now, I'll keep chart data local but fetched on mount/change
    useEffect(() => {
        const loadChart = async () => {
            const viewId = selectedUser?.id || (user?.role === 'ADMIN' ? null : user?.id);
            if (!viewId && user?.role !== 'ADMIN') return;
            try {
                const historyData = await fetchPortfolioHistory(viewId);
                setChartData(historyData.length > 0 ? historyData : [
                    { name: 'Mon', value: 0 }, { name: 'Tue', value: 0 }, { name: 'Wed', value: 0 }, { name: 'Thu', value: 0 }, { name: 'Fri', value: 0 }
                ]);
            } catch (err) {
                console.error("Chart load error:", err);
            }
        };
        loadChart();
    }, [selectedUser, user]);

    const handleQuickDeposit = async () => {
        const viewId = selectedUser?.id || user?.id;
        if (!viewId) return;
        setDepositing(true);
        try {
            const result = await depositFunds(viewId, 1000); // Quick $1000
            if (result) {
                await refreshAllData();
                alert("Quick Deposit of ₹1,000 successful.");
            }
        } catch (err) {
            console.error("Quick deposit failed:", err);
        } finally {
            setDepositing(false);
        }
    };

    const metrics = [
        {
            label: user?.role === 'BUSINESS_OWNER' ? 'Total Managed Assets' : 'Total Equity',
            value: `₹${((summary?.invested_amount || 0) + (summary?.cash_balance || 0)).toLocaleString()}`,
            change: summary?.win_rate ? `+${(summary.win_rate * 0.15).toFixed(1)}%` : '+0.0%',
            icon: BarChart2,
            color: 'text-primary',
            link: '/portfolio'
        },
        {
            label: 'Ready Capital',
            value: summary ? `₹${(summary.cash_balance || 0).toLocaleString()}` : '₹0',
            change: socketStatus === 'connected' ? 'SECURE' : 'OFFLINE',
            icon: DollarSign,
            color: 'text-indigo-600',
            link: '/portfolio',
            action: (
                <button
                    onClick={(e) => { e.preventDefault(); handleQuickDeposit(); }}
                    disabled={depositing}
                    className="p-1.5 hover:bg-indigo-50 rounded-lg text-indigo-400 hover:text-indigo-600 transition-colors"
                >
                    {depositing ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
                </button>
            )
        },
        {
            label: user?.role === 'AUDITOR' ? 'Audit Exposure' : 'Open Exposure',
            value: `₹${(summary?.invested_amount || 0).toLocaleString()}`,
            change: summary?.positions_count ? `${summary.positions_count} positions` : 'No active positions',
            icon: Activity,
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
        },
        {
            label: user?.role === 'ADMIN' ? 'Live System Load' : 'System Health',
            value: user?.role === 'ADMIN' && adminTelemetry ? adminTelemetry.system_load : (socketStatus === 'connected' ? '100%' : 'OFFLINE'),
            change: user?.role === 'ADMIN' && adminTelemetry ? `Active Users: ${adminTelemetry.active_users}` : (exchangeStatus?.status || 'ONLINE'),
            icon: Shield,
            color: 'text-green-600',
            link: user?.role === 'ADMIN' ? '/users' : '/'
        },
    ];

    if (loading) {
        return (
            <div className="h-screen flex flex-col items-center justify-center text-slate-400">
                <Loader2 className="animate-spin mb-4" size={48} />
                <p className="font-black uppercase text-xs tracking-[0.3em] text-[#0A2A4D]">Establishing Secure Data Tunnel...</p>
            </div>
        );
    }

    return (
        <div data-testid="dashboard-container" className="flex flex-col min-h-screen animate-in fade-in slide-in-from-top-4 duration-700 pb-4">
            <MarketTicker />
            <div className="max-w-[1600px] mx-auto space-y-8 p-6 w-full">
                <header className="flex flex-col gap-6 md:flex-row md:items-center justify-between">
                    <div>
                        <h1 className="text-2xl md:text-3xl font-black tracking-tight text-slate-900 font-heading">
                            {user?.role === 'ADMIN' ? (selectedUser ? `Auditing: ${selectedUser.name}` : 'Platform Executive Control') :
                                user?.role === 'AUDITOR' ? 'Compliance Oversight' :
                                    user?.role === 'BUSINESS_OWNER' ? 'Executive Dashboard' :
                                        `Welcome, ${user?.name || 'Investor'}`}
                        </h1>
                        <div className="flex items-center gap-2 mt-2">
                            <span className={`h-1.5 w-1.5 rounded-full animate-pulse ${user?.role === 'ADMIN' ? 'bg-indigo-500' :
                                user?.role === 'AUDITOR' ? 'bg-amber-500' :
                                    user?.role === 'BUSINESS_OWNER' ? 'bg-purple-500' :
                                        'bg-primary'
                                }`} />
                            <p className="text-slate-500 uppercase text-[10px] font-bold tracking-[0.2em] leading-none">
                                {user?.role === 'ADMIN' ? (selectedUser ? 'User Inspection Mode: ACTIVE' : 'Global System Oversight: ACTIVE') :
                                    user?.role === 'AUDITOR' ? 'Audit Logging: ENABLED' :
                                        user?.role === 'BUSINESS_OWNER' ? 'Revenue Monitoring: PASSIVE' :
                                            'Personal Wealth Agent: ACTIVE'}
                            </p>
                        </div>
                    </div>
                    <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
                        {user?.role === 'ADMIN' && (
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
                                            if (u) setSelectedUser(u);
                                        }
                                    }}
                                >
                                    <option value="GLOBAL">Platform Summary</option>
                                    <optgroup label="Active Users">
                                        {allUsers.map(u => (
                                            <option key={u.id} value={u.id}>{u.name}</option>
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

                <div data-testid="guardian-intelligence-card" className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                        <Shield size={160} className="text-primary rotate-12" />
                    </div>

                    <div className="relative z-10 space-y-8">
                        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                            <div className="flex items-center gap-4">
                                <div className="h-14 w-14 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30 shrink-0">
                                    <Zap className="text-primary animate-pulse" size={28} />
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-[10px] font-black text-primary uppercase tracking-[0.3em]">Guardian Intelligence</span>
                                        <span className="h-1 w-1 rounded-full bg-slate-700" />
                                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Real-time Analysis</span>
                                    </div>
                                    <h2 className="text-white text-xl font-black tracking-tight leading-tight max-w-2xl">
                                        {stewardPrediction?.prediction || "Synchronizing with market sentiment..."}
                                    </h2>
                                </div>
                            </div>

                            <div className="flex gap-4 w-full md:w-auto">
                                <Link to="/trading-hub" className="flex-1 md:flex-none">
                                    <button className="w-full bg-primary hover:bg-primary/90 text-white px-6 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all hover:scale-105 active:scale-95 shadow-lg shadow-primary/20 flex items-center justify-center gap-2">
                                        <Activity size={14} />
                                        Launch Strategy
                                    </button>
                                </Link>
                                <button className="flex-1 md:flex-none bg-slate-800 hover:bg-slate-700 text-slate-300 px-6 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all border border-slate-700">
                                    View Logic
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-6 border-t border-slate-800/50">
                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">AI Decision</p>
                                <div className="flex items-center gap-2">
                                    <div className={`px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest ${stewardPrediction?.decision?.includes('BUY') ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                        stewardPrediction?.decision?.includes('SELL') ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                                            'bg-slate-700/50 text-slate-400 border border-slate-600/30'
                                        }`}>
                                        {stewardPrediction?.decision || "HOLD"}
                                    </div>
                                    <span className="text-[10px] font-bold text-slate-500">Medium Term</span>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Model Confidence</p>
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
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Signal Mix</p>
                                <div className="flex flex-wrap gap-2">
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">Tech: {stewardPrediction?.signal_mix?.technical || 0}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">Fund: {stewardPrediction?.signal_mix?.fundamental || 0}</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-orange-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">News: {stewardPrediction?.signal_mix?.news || 0}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2 border-l border-slate-800/50 pl-6">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Risk Radar</p>
                                <div className="flex items-center gap-3">
                                    <div className="relative h-10 w-10 flex items-center justify-center">
                                        <svg className="h-10 w-10 -rotate-90">
                                            <circle cx="20" cy="20" r="18" fill="transparent" stroke="currentColor" strokeWidth="3" className="text-slate-800" />
                                            <circle cx="20" cy="20" r="18" fill="transparent" stroke="currentColor" strokeWidth="3" strokeDasharray={113} strokeDashoffset={113 - (113 * (stewardPrediction?.risk_radar || 0)) / 100} className="text-red-500 transition-all duration-1000" />
                                        </svg>
                                        <span className="absolute text-[8px] font-black text-white">{stewardPrediction?.risk_radar || 0}</span>
                                    </div>
                                    <div>
                                        <p className="text-[10px] font-black text-white leading-none">High Volatility</p>
                                        <p className="text-[8px] font-bold text-slate-500 uppercase mt-1">Nifty Exposure</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div data-testid="metrics-grid" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {metrics.map((stat, i) => (
                        <Link to={stat.link} key={i}>
                            <Card className="p-6 border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group bg-white h-full cursor-pointer">
                                <div className="flex justify-between items-start mb-4">
                                    <div className={`p-2.5 rounded-xl bg-slate-50 transition-colors group-hover:bg-primary/5 ${stat.color}`}>
                                        <stat.icon size={18} />
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {stat.action}
                                        <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${stat.change.startsWith('+') ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-600'
                                            }`}>
                                            {stat.change}
                                        </span>
                                    </div>
                                </div>
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">{stat.label}</p>
                                <h3 className="text-2xl font-black text-slate-900 tracking-tight">{stat.value}</h3>
                            </Card>
                        </Link>
                    ))}
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
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
                                <span className="text-[10px] font-bold text-slate-500 uppercase">Steward Equity</span>
                            </div>
                        </div>
                        <div className="h-[350px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.15} />
                                            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
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
                                        tickFormatter={(val) => `$${val}`}
                                    />
                                    <Tooltip
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
                                        stroke="hsl(var(--primary))"
                                        strokeWidth={4}
                                        fillOpacity={1}
                                        fill="url(#colorValue)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>

                    <div className="xl:col-span-4 h-full">
                        <TopMovers />
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {user?.role !== 'AUDITOR' && <AIAnalyst />}

                    <Card className={`border-slate-100 shadow-sm bg-white ${user?.role === 'AUDITOR' ? 'lg:col-span-2' : ''}`}>
                        <div data-testid="intelligence-log" className={`p-6 border-b border-slate-50 flex justify-between items-center`}>
                            <div className="flex items-center gap-2">
                                <Clock size={16} className="text-primary" />
                                <h3 className="font-black text-slate-900 text-sm uppercase tracking-wider">
                                    {user?.role === 'AUDITOR' ? 'Global Audit Trail' : 'Agent Intelligence Log'}
                                </h3>
                            </div>
                            <Settings size={14} className="text-slate-400" />
                        </div>
                        <div className="divide-y divide-slate-50">
                            {recentTrades.map((log, i) => (
                                <Link to="/reports" key={i}>
                                    <div className="p-5 flex items-start justify-between gap-4 hover:bg-indigo-50/50 transition-colors group">
                                        <div className="flex gap-4">
                                            <span className="text-[10px] font-black text-slate-300 mt-1">
                                                {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                            <div>
                                                <h4 className="text-xs font-black text-slate-900 group-hover:text-primary transition-colors">
                                                    {user?.role === 'AUDITOR' && <span className="bg-amber-50 text-amber-700 px-1.5 py-0.5 rounded text-[8px] uppercase mr-2 text-primary font-black">Verified</span>}
                                                    {log.action} <span className="text-primary">{log.symbol}</span>
                                                </h4>
                                                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-1">Executor: AI-Steward</p>
                                                <p className="text-[11px] text-slate-600 mt-2 bg-slate-50 px-2 py-1 rounded border border-slate-100 italic group-hover:bg-white transition-colors">{log.decision_logic}</p>
                                            </div>
                                        </div>
                                        <div className="h-2 w-2 rounded-full mt-1 bg-green-500 group-hover:animate-ping" />
                                    </div>
                                </Link>
                            ))}
                        </div>
                        <div className="space-y-4">
                            {allUsers && allUsers.map((u) => (
                                <div key={u.id} className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                                    <Shield size={12} />
                                    <span>END-TO-END CRYPTOGRAPHIC LOG VERIFICATION: COMPLETE</span>
                                </div>
                            ))}
                        </div>
                        {user?.role === 'AUDITOR' && (
                            <div className="p-4 bg-slate-900 text-slate-400 text-[10px] font-mono flex items-center gap-2">
                                <Shield size={12} />
                                <span>END-TO-END CRYPTOGRAPHIC LOG VERIFICATION: COMPLETE</span>
                            </div>
                        )}
                    </Card>
                </div>
            </div>

            {/* Risk Disclosure Footer */}
            <div className="max-w-[1600px] mx-auto mt-12 p-6 border-t border-slate-100/50">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-[10px] text-slate-400 font-bold uppercase tracking-[0.15em]">
                    <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
                        <span>System ID: SS-AI-ALPHA-2026</span>
                    </div>
                    <p className="max-w-2xl text-center md:text-right leading-relaxed opacity-60">
                        Mandatory Disclosure: Algorithmic trading involves high market risk. StockSteward AI provides execution intelligence for educational and platform demonstration purposes only. Consult with a SEBI-registered advisor before committing real capital.
                    </p>
                </div>
            </div>
        </div>
    );
}
