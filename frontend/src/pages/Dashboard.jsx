import React, { useState, useEffect } from 'react';
import { Card } from "../components/ui/card";
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis,
    CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import {
    ArrowUpRight, ArrowDownRight, Activity,
    TrendingUp, Shield, BarChart2, Clock,
    AlertCircle, Search, Settings, Loader2
} from 'lucide-react';
import { AIAnalyst } from "../components/AIAnalyst";
import { fetchPortfolioSummary, fetchTrades } from "../services/api";

// Fallback static data for charts
const performanceData = [
    { name: 'Mon', value: 4000 },
    { name: 'Tue', value: 3000 },
    { name: 'Wed', value: 2000 },
    { name: 'Thu', value: 2780 },
    { name: 'Fri', value: 1890 },
    { name: 'Sat', value: 2390 },
    { name: 'Sun', value: 3490 },
];

const marketMovers = [
    { symbol: 'TSLA', change: '+3.2%', type: 'up' },
    { symbol: 'AAPL', change: '-1.4%', type: 'down' },
    { symbol: 'NVDA', change: '+2.8%', type: 'up' },
    { symbol: 'MSFT', change: '+0.9%', type: 'up' },
];

export function Dashboard() {
    const [period, setPeriod] = useState('Today');
    const [summary, setSummary] = useState(null);
    const [recentTrades, setRecentTrades] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [sumData, tradeData] = await Promise.all([
                    fetchPortfolioSummary(1),
                    fetchTrades()
                ]);
                setSummary(sumData);
                setRecentTrades(tradeData.slice(0, 3));
            } catch (err) {
                console.error("Dashboard Load Error:", err);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) {
        return (
            <div className="h-screen flex flex-col items-center justify-center text-slate-400">
                <Loader2 className="animate-spin mb-4" size={48} />
                <p className="font-black uppercase text-xs tracking-[0.3em] text-[#0A2A4D]">Establishing Secure Data Tunnel...</p>
            </div>
        );
    }

    const metrics = [
        { label: 'Total Equity', value: `$${((summary?.invested_amount || 0) + (summary?.cash_balance || 0)).toLocaleString()}`, change: '+14.2%', icon: BarChart2, color: 'text-primary' },
        { label: 'Open Exposure', value: `$${(summary?.invested_amount || 0).toLocaleString()}`, change: '8 positions', icon: Activity, color: 'text-indigo-600' },
        { label: 'Daily Alpha', value: `+${summary?.win_rate || 0}%`, change: 'Beat SPY by 2%', icon: TrendingUp, color: 'text-primary' },
        { label: 'System Health', value: '100%', change: 'Latency 42ms', icon: Shield, color: 'text-green-600' },
    ];


    const [chartData, setChartData] = useState(performanceData);

    useEffect(() => {
        const fetchChartData = async () => {
            // Mock fetching history for now as per backend availability, 
            // but structured to accept real data
            try {
                // In a real app: const history = await fetchPortfolioHistory(1);
                // For now, we simulate dynamic slicing of the static data or extended mock data

                // Stimulate data change based on period
                let data = [...performanceData];
                if (period === 'Today') {
                    // Hourly granularity simulation
                    data = [
                        { name: '9AM', value: 4000 },
                        { name: '10AM', value: 4200 },
                        { name: '11AM', value: 4100 },
                        { name: '12PM', value: 4300 },
                        { name: '1PM', value: 4250 },
                        { name: '2PM', value: 4400 },
                    ];
                } else if (period === 'This Week') {
                    // Daily
                    data = performanceData;
                } else {
                    // Monthly simulation
                    data = [
                        { name: 'Jan', value: 4000 },
                        { name: 'Feb', value: 5500 },
                        { name: 'Mar', value: 4800 },
                        { name: 'Apr', value: 6200 },
                    ];
                }
                setChartData(data);
            } catch (e) {
                console.error("Chart data error", e);
            }
        };
        fetchChartData();
    }, [period]);

    return (
        <div className="max-w-[1600px] mx-auto space-y-8 animate-in fade-in slide-in-from-top-4 duration-700 pb-12">
            {/* Headers and Metrics... */}
            {/* Minimalist Top Header */}
            <header className="flex flex-col gap-6 md:flex-row md:items-center justify-between">
                <div>
                    <h1 className="text-2xl md:text-3xl font-black tracking-tight text-slate-900 font-heading">Executive Overview</h1>
                    <div className="flex items-center gap-2 mt-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
                        <p className="text-slate-500 uppercase text-[10px] font-bold tracking-[0.2em] leading-none">Live Agent Streaming Status: ACTIVE</p>
                    </div>
                </div>
                <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 self-start w-full md:w-auto overflow-x-auto">
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
            </header>

            {/* Core Metrics... (Unchanged logic, just ensuring context is kept) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {metrics.map((stat, i) => (
                    <Card key={i} className="p-6 border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group bg-white">
                        <div className="flex justify-between items-start mb-4">
                            <div className={`p-2.5 rounded-xl bg-slate-50 transition-colors group-hover:bg-primary/5 ${stat.color}`}>
                                <stat.icon size={18} />
                            </div>
                            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${stat.change.startsWith('+') ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-600'
                                }`}>
                                {stat.change}
                            </span>
                        </div>
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">{stat.label}</p>
                        <h3 className="text-2xl font-black text-slate-900 tracking-tight">{stat.value}</h3>
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
                {/* Main Curve */}
                <Card className="xl:col-span-8 p-8 border-slate-100 shadow-sm bg-white overflow-hidden relative">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-lg font-black text-slate-900 font-heading">Performance Alpha</h2>
                            <p className="text-xs text-slate-500 font-medium">Net performance curve across all active strategies</p>
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

                {/* Market Movers - professional Sidebar */}
                <Card className="xl:col-span-4 border-slate-100 shadow-sm bg-white overflow-hidden">
                    <div className="p-6 border-b border-slate-50 flex justify-between items-center">
                        <h3 className="font-black text-slate-900 text-sm uppercase tracking-wider">Top Movers</h3>
                        <Search size={14} className="text-slate-400" />
                    </div>
                    <div className="p-2">
                        {marketMovers.map((mover, i) => (
                            <div key={i} className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors rounded-xl cursor-pointer">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center font-black text-slate-900 text-xs">
                                        {mover.symbol}
                                    </div>
                                    <div>
                                        <p className="text-xs font-black text-slate-900">{mover.symbol} Inc.</p>
                                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">NASD</p>
                                    </div>
                                </div>
                                <div className={`flex items-center gap-1 font-black text-xs ${mover.type === 'up' ? 'text-green-600' : 'text-red-500'
                                    }`}>
                                    {mover.type === 'up' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                                    {mover.change}
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="p-4 mt-2">
                        <button className="w-full py-3 text-xs font-black text-slate-500 hover:text-slate-900 uppercase tracking-widest transition-colors">View All Volatility Focus</button>
                    </div>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* AI Prediction Insight */}
                <AIAnalyst />

                {/* Audit log - Trimmed */}
                <Card className="border-slate-100 shadow-sm bg-white">
                    <div className="p-6 border-b border-slate-50 flex justify-between items-center">
                        <div className="flex items-center gap-2">
                            <Clock size={16} className="text-primary" />
                            <h3 className="font-black text-slate-900 text-sm uppercase tracking-wider">Agent Intelligence Log</h3>
                        </div>
                        <Settings size={14} className="text-slate-400" />
                    </div>
                    <div className="divide-y divide-slate-50">
                        {recentTrades.map((log, i) => (
                            <div key={i} className="p-5 flex items-start justify-between gap-4 hover:bg-slate-50/50 transition-colors">
                                <div className="flex gap-4">
                                    <span className="text-[10px] font-black text-slate-300 mt-1">
                                        {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                    <div>
                                        <h4 className="text-xs font-black text-slate-900">{log.action} <span className="text-primary">{log.symbol}</span></h4>
                                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-1">Executor: AI-Steward</p>
                                        <p className="text-[11px] text-slate-600 mt-2 bg-slate-50 px-2 py-1 rounded border border-slate-100 italic">{log.decision_logic}</p>
                                    </div>
                                </div>
                                <div className="h-2 w-2 rounded-full mt-1 bg-green-500" />
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
}
