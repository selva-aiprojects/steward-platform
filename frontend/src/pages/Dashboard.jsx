import React, { useState } from 'react';
import {
    TrendingUp,
    TrendingDown,
    Activity,
    BarChart3,
    Shield,
    DollarSign,
    Zap
} from 'lucide-react';
import CompactTicker from '../components/CompactTicker';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import { Link } from 'react-router-dom';
import { Card } from '../components/ui/card';
import { useUser } from '../context/UserContext';
import { useAppData } from '../context/AppDataContext';

export function Dashboard() {
    const [period, setPeriod] = useState('This Week');

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

    const formatNumber = (value, digits = 2) => {
        const num = typeof value === 'number' ? value : parseFloat(value);
        if (!Number.isFinite(num)) return '0.00';
        return num.toFixed(digits);
    };

    const formatPrice = (value) => {
        if (value === null || value === undefined) return 'INR --';
        const num = typeof value === 'number' ? value : parseFloat(value);
        if (!Number.isFinite(num) || num === 0) return 'INR --';
        return `INR ${num.toLocaleString()}`;
    };

    const exchangeClass = (exchange) => {
        switch ((exchange || '').toUpperCase()) {
            case 'NSE':
                return 'text-emerald-300 border-emerald-500/60';
            case 'BSE':
                return 'text-sky-300 border-sky-500/60';
            case 'MCX':
                return 'text-amber-300 border-amber-500/60';
            default:
                return 'text-slate-300 border-slate-500/60';
        }
    };

    const currentStewardPrediction = stewardPredictionState || {
        prediction: '',
        decision: '',
        confidence: 0,
        signal_mix: { technical: 0, fundamental: 0, news: 0 },
        risk_radar: 0
    };

    // Live movers
    const mm = marketMoversState || { gainers: [], losers: [] };
    const gainers = Array.isArray(mm.gainers) ? mm.gainers : [];
    const losers = Array.isArray(mm.losers) ? mm.losers : [];

    // Tickers: take more stocks for the compact ticker display
    const groupedStocks = [...gainers, ...losers].slice(0, 10);

    // Currencies: from live movers only (symbols ending with INR)
    const currencyItems = (() => {
        const all = [...gainers, ...losers];
        return all
            .filter(
                (s) =>
                    s &&
                    s.symbol &&
                    String(s.symbol).toUpperCase().endsWith('INR') &&
                    Number.isFinite(Number(s.price))
            )
            .slice(0, 8);
    })();

    // IPO news: from live marketNews only
    const ipoNews = (() => {
        const news = Array.isArray(marketNews) ? marketNews : [];
        return news
            .filter((n) => {
                const text = [n?.title, n?.headline, n?.summary, n?.content]
                    .filter(Boolean)
                    .join(' ')
                    .toLowerCase();
                return text.includes('ipo') || text.includes('listing');
            })
            .slice(0, 6);
    })();

    // Live curve from backend (if available)
    const chartData =
        Array.isArray(macroIndicators?.equity_curve) && macroIndicators.equity_curve.length
            ? macroIndicators.equity_curve
            : [];

    if (loading) {
        return (
            <div className="h-screen flex flex-col items-center justify-center text-slate-400">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
                <p className="font-black uppercase text-xs tracking-[0.3em] text-slate-500 mt-4">
                    LOADING DASHBOARD...
                </p>
            </div>
        );
    }

    const metrics = [
        {
            label: user?.role === 'BUSINESS_OWNER' ? 'Total Managed Assets' : 'Total Equity',
            value: `INR ${(
                (summary?.invested_amount || 0) + (summary?.cash_balance || 0)
            ).toLocaleString()}`,
            change: summary?.win_rate ? `+${(summary.win_rate * 0.15).toFixed(1)}%` : '+0.0%',
            icon: BarChart3,
            color: 'text-primary',
            link: '/portfolio'
        },
        {
            label: 'Ready Capital',
            value: `INR ${(summary?.cash_balance || 0).toLocaleString()}`,
            change: summary?.socket_status || 'LIVE',
            icon: DollarSign,
            color: 'text-indigo-600',
            link: '/portfolio'
        },
        {
            label: user?.role === 'AUDITOR' ? 'Audit Exposure' : 'Open Exposure',
            value: `INR ${(summary?.invested_amount || 0).toLocaleString()}`,
            change: summary?.positions_count ? `${summary.positions_count} positions` : 'No active positions',
            icon: Activity,
            color: 'text-indigo-600',
            link: '/portfolio'
        },
        {
            label: user?.role === 'BUSINESS_OWNER' ? 'Portfolio ROI' : 'Daily Alpha',
            value: summary?.win_rate != null ? `+${summary.win_rate}%` : '--',
            change:
                summary?.win_rate != null ? `Win rate ${summary.win_rate}%` : 'Awaiting live trades',
            icon: TrendingUp,
            color: 'text-primary',
            link: '/reports'
        }
    ];

    return (
        <div className="flex flex-col min-h-screen pb-4">
            <div className="max-w-[1600px] mx-auto space-y-8 p-6 w-full">
                {/* Header */}
                <header className="flex flex-col gap-6 md:flex-row md:items-center justify-between">
                    <div>
                        <h1 className="text-2xl md:text-3xl font-black tracking-tight text-slate-900 font-heading">
                            {user?.role === 'SUPERADMIN'
                                ? selectedUser
                                    ? `Auditing: ${
                                        selectedUser.name || selectedUser.full_name || selectedUser.email
                                    }`
                                    : 'Platform Executive Control'
                                : user?.role === 'AUDITOR'
                                    ? 'Compliance Oversight'
                                    : user?.role === 'BUSINESS_OWNER'
                                        ? 'Executive Dashboard'
                                        : `Welcome, ${user?.name || 'Investor'}`}
                        </h1>
                        <div className="flex items-center gap-2 mt-2">
              <span
                  className={`h-1.5 w-1.5 rounded-full animate-pulse ${
                      user?.role === 'SUPERADMIN'
                          ? 'bg-indigo-500'
                          : user?.role === 'AUDITOR'
                              ? 'bg-amber-500'
                              : user?.role === 'BUSINESS_OWNER'
                                  ? 'bg-purple-500'
                                  : 'bg-primary'
                  }`}
              />
                            <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] leading-none">
                                {user?.role === 'SUPERADMIN'
                                    ? selectedUser
                                        ? 'User Inspection Mode: LIVE'
                                        : 'Global System Oversight: LIVE'
                                    : user?.role === 'AUDITOR'
                                        ? 'Audit Logging: LIVE'
                                        : user?.role === 'BUSINESS_OWNER'
                                            ? 'Revenue Monitoring: LIVE'
                                            : 'Personal Wealth Agent: LIVE'}
                            </p>
                        </div>
                    </div>

                    <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
                        {isAdmin && (
                            <div className="flex items-center gap-3 bg-white border border-slate-200 p-1.5 rounded-xl shadow-sm">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-2">
                  Scope
                </span>
                                <select
                                    className="bg-slate-50 border-none text-[10px] font-black uppercase tracking-widest text-slate-700 focus:ring-0 rounded-lg py-1 px-3 cursor-pointer"
                                    value={selectedUser?.id || 'GLOBAL'}
                                    onChange={(e) => {
                                        const val = e.target.value;
                                        if (val === 'GLOBAL') {
                                            setSelectedUser(null);
                                        } else {
                                            const u = allUsers.find((usr) => usr.id === parseInt(val));
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
                                        {allUsers.map((u) => (
                                            <option key={u.id} value={u.id}>
                                                {u.full_name || u.name || u.email}
                                            </option>
                                        ))}
                                    </optgroup>
                                </select>
                            </div>
                        )}

                        <div className="flex bg-slate-100 p-1.5 rounded-xl border border-slate-200 w-full md:w-auto overflow-x-auto">
                            {['Today', 'This Week', 'This Year'].map((p) => (
                                <button
                                    key={p}
                                    onClick={() => setPeriod(p)}
                                    className={`flex-1 md:flex-none px-4 py-2 text-xs font-black rounded-lg transition-all whitespace-nowrap ${
                                        period === p ? 'bg-white shadow-md text-primary' : 'text-slate-400 hover:text-slate-700'
                                    }`}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>

                        <button
                            onClick={refreshAllData}
                            className="px-4 py-2 text-[10px] font-black rounded-lg bg-slate-900 text-white uppercase tracking-[0.2em]"
                        >
                            Refresh Live Data
                        </button>
                    </div>
                </header>

                {/* AI Intelligence Card */}
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                        <Shield size={160} className="text-primary rotate-12" />
                    </div>

                    <div className="relative z-10 space-y-8">
                        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                            <div className="flex items-center gap-4">
                                <div className="h-14 w-14 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30 shadow-sm">
                                    <Zap className="text-primary animate-pulse" size={28} />
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-black text-primary uppercase tracking-[0.3em]">
                      GUARDIAN INTELLIGENCE
                    </span>
                                        <span className="h-1 w-1 rounded-full bg-slate-700" />
                                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                      REAL-TIME ANALYSIS
                    </span>
                                    </div>
                                    <h2 className="text-white text-xl font-black tracking-tight leading-tight max-w-2xl">
                                        {currentStewardPrediction?.prediction || 'Waiting for live model signal...'}
                                    </h2>
                                </div>
                            </div>

                            <div className="flex gap-4 w-full md:w-auto">
                                <Link to="/trading" className="flex-1 md:flex-none">
                                    <button className="w-full bg-primary hover:bg-primary/90 text-white px-6 py-3.5 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all hover:scale-105 active:scale-95 shadow-lg shadow-primary/20 flex items-center justify-center gap-2">
                                        <Activity size={14} />
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
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                    AI DECISION
                                </p>
                                <div
                                    className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest ${
                                        currentStewardPrediction?.decision?.includes('BUY')
                                            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                            : currentStewardPrediction?.decision?.includes('SELL')
                                                ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                                                : 'bg-slate-700/50 text-slate-400 border border-slate-600/30'
                                    }`}
                                >
                                    {currentStewardPrediction?.decision || 'HOLD'}
                                </div>
                                <span className="text-[10px] font-bold text-slate-500">MEDIUM TERM</span>
                            </div>

                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                    MODEL CONFIDENCE
                                </p>
                                <div className="flex items-center gap-3">
                  <span className="text-xl font-black text-white">
                    {currentStewardPrediction?.confidence || 0}%
                  </span>
                                    <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary transition-all duration-1000"
                                            style={{ width: `${currentStewardPrediction?.confidence || 0}%` }}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                    SIGNAL MIX
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">
                      TECH: {currentStewardPrediction?.signal_mix?.technical || 0}
                    </span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">
                      FUND: {currentStewardPrediction?.signal_mix?.fundamental || 0}
                    </span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <div className="h-1.5 w-1.5 rounded-full bg-orange-500" />
                                        <span className="text-[9px] font-bold text-slate-400 uppercase">
                      NEWS: {currentStewardPrediction?.signal_mix?.news || 0}
                    </span>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2 border-l border-slate-800/50 pl-6">
                                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                    RISK RADAR
                                </p>
                                <div className="flex items-center gap-3">
                                    <div className="relative h-10 w-10 flex items-center justify-center">
                                        <svg className="h-10 w-10 -rotate-90">
                                            <circle
                                                cx="20"
                                                cy="20"
                                                r="18"
                                                fill="transparent"
                                                stroke="currentColor"
                                                strokeWidth="3"
                                                className="text-slate-800"
                                            />
                                            <circle
                                                cx="20"
                                                cy="20"
                                                r="18"
                                                fill="transparent"
                                                stroke="currentColor"
                                                strokeWidth="3"
                                                strokeDasharray={113}
                                                strokeDashoffset={
                                                    113 - (113 * (currentStewardPrediction?.risk_radar || 0)) / 100
                                                }
                                                className="text-red-500 transition-all duration-1000"
                                            />
                                        </svg>
                                        <span className="absolute text-[8px] font-black text-white">
                      {currentStewardPrediction?.risk_radar || 0}
                    </span>
                                    </div>
                                    <div>
                                        <p className="text-[10px] font-black text-white leading-none">
                                            HIGH VOLATILITY
                                        </p>
                                        <p className="text-[8px] font-bold text-slate-500 uppercase mt-1">
                                            NIFTY EXPOSURE
                                        </p>
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
                                    <div
                                        className={`p-2.5 rounded-xl bg-slate-50 transition-colors group-hover:bg-primary/5 ${metric.color}`}
                                    >
                                        <metric.icon size={18} />
                                    </div>
                                    <span
                                        className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                                            metric.change.startsWith('+') || metric.change.includes('LIVE')
                                                ? 'bg-green-50 text-green-700'
                                                : 'bg-slate-100 text-slate-600'
                                        }`}
                                    >
                    {metric.change}
                  </span>
                                </div>
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">
                                    {metric.label}
                                </p>
                                <h3 className="text-2xl font-black text-slate-900 tracking-tight">
                                    {metric.value}
                                </h3>
                            </Card>
                        </Link>
                    ))}
                </div>

                {/* Compact Live Ticker Strip */}
                <CompactTicker stocks={groupedStocks} title="LIVE MARKET DATA" height="h-12" />

                {/* FX + IPO cards */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="p-6 bg-white border border-slate-100 shadow-sm">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-heading font-black text-slate-900 text-base">Currencies</h3>
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                FX PAIRS
              </span>
                        </div>
                        <div className="flex gap-4 overflow-x-auto pb-2">
                            {currencyItems.length === 0 ? (
                                <span className="text-[10px] font-bold text-slate-400">No FX data</span>
                            ) : (
                                currencyItems.map((item, i) => {
                                    const change = Number(item.change || 0);
                                    const isUp = change >= 0;
                                    const price = Number(item.price);
                                    return (
                                        <div
                                            key={i}
                                            className="min-w-[180px] px-4 py-3 rounded-xl bg-slate-900 text-white border border-slate-800"
                                        >
                                            <div className="flex items-center justify-between mb-1">
                        <span className="text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border border-slate-700">
                          {item.symbol.slice(0, -3)} INR
                        </span>
                                                <span
                                                    className={`text-[10px] font-black ${
                                                        isUp ? 'text-emerald-400' : 'text-red-400'
                                                    }`}
                                                >
                          {isUp ? '+' : ''}
                                                    {change.toFixed(2)}%
                        </span>
                                            </div>
                                            <div className="text-sm font-bold">
                                                ₹{' '}
                                                {Number.isFinite(price) && price !== 0
                                                    ? price.toLocaleString('en-IN', { maximumFractionDigits: 2 })
                                                    : '--'}
                                            </div>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </Card>

                    <Card className="p-6 bg-white border border-slate-100 shadow-sm">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-heading font-black text-slate-900 text-base">New IPOs</h3>
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                LISTINGS
              </span>
                        </div>
                        <div className="space-y-3">
                            {ipoNews.length === 0 ? (
                                <div className="text-xs text-slate-400 italic">No IPO news available</div>
                            ) : (
                                ipoNews.map((n, i) => (
                                    <div key={i} className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                                        <p className="text-sm font-bold text-slate-900">
                                            {n.title || n.headline || 'IPO Announcement'}
                                        </p>
                                        {n.date && (
                                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">
                                                {n.date}
                                            </p>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </Card>
                </div>

                {/* Chart + AI Analyst + Top Movers */}
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
                    <Card className="xl:col-span-8 p-8 border-slate-100 shadow-sm bg-white overflow-hidden relative">
                        <div className="flex items-center justify-between mb-8">
                            <div>
                                <h2 className="text-lg font-black text-slate-900 font-heading">
                                    {user?.role === 'AUDITOR' ? 'Compliance Alpha Curve' : 'Performance Alpha'}
                                </h2>
                                <p className="text-xs text-slate-500 font-medium">
                                    {user?.role === 'AUDITOR'
                                        ? 'System execution integrity audit'
                                        : 'Net performance curve across all active strategies'}
                                </p>
                            </div>
                            <div className="flex gap-2">
                                <div className="h-3 w-3 rounded-full bg-primary" />
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
                  Steward Equity
                </span>
                            </div>
                        </div>
                        <div className="h-[350px] w-full">
                            {chartData.length === 0 ? (
                                <div className="h-full flex items-center justify-center text-xs text-slate-400">
                                    No live curve data
                                </div>
                            ) : (
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
                            )}
                        </div>
                    </Card>

                    <div className="xl:col-span-4 space-y-6">
                        <Card className="p-6 border-slate-100 shadow-sm bg-white">
                            <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">
                                AI Analyst Insights
                            </h3>
                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                                    <p className="text-xs text-slate-700 leading-relaxed">
                                        {currentStewardPrediction?.prediction ||
                                            'AI is analyzing market conditions and generating insights...'}
                                    </p>
                                </div>
                                <div className="flex justify-between text-xs">
                                    <span className="text-slate-500">Market Sentiment</span>
                                    <span className="font-black text-primary">
                    {macroIndicators?.sentiment || 'NEUTRAL'}
                  </span>
                                </div>
                                <div className="flex justify-between text-xs">
                                    <span className="text-slate-500">Volatility Level</span>
                                    <span className="font-black text-amber-500">
                    {macroIndicators?.volatility_label || 'UNKNOWN'}
                  </span>
                                </div>
                            </div>
                        </Card>

                        <Card className="p-6 border-slate-100 shadow-sm bg-white">
                            <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">
                                Top Movers
                            </h3>
                            <div className="space-y-3">
                                {gainers.slice(0, 3).map((mover, i) => (
                                    <div key={i} className="flex justify-between items-center">
                                        <div>
                                            <p className="font-black text-slate-900">{mover.symbol}</p>
                                            <p className="text-[10px] text-slate-500">
                                                +{formatNumber(mover.change || 0, 2)}%
                                            </p>
                                        </div>
                                        <p className="font-black text-green-600">{formatPrice(mover.price)}</p>
                                    </div>
                                ))}
                                {losers.slice(0, 2).map((mover, i) => (
                                    <div key={i} className="flex justify-between items-center">
                                        <div>
                                            <p className="font-black text-slate-900">{mover.symbol}</p>
                                            <p className="text-[10px] text-slate-500">
                                                {formatNumber(mover.change || 0, 2)}%
                                            </p>
                                        </div>
                                        <p className="font-black text-red-500">{formatPrice(mover.price)}</p>
                                    </div>
                                ))}
                                {gainers.length === 0 && losers.length === 0 && (
                                    <div className="text-xs text-slate-400 italic">No live movers data</div>
                                )}
                            </div>
                        </Card>
                    </div>
                </div>

                {/* Market Intelligence + Order Book + Exchange Status */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <Card className="p-6 border-slate-100 shadow-sm bg-white">
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">
                            Market Intelligence
                        </h3>
                        <div className="space-y-3">
                            {(marketResearch?.headlines || []).slice(0, 5).map((headline, i) => (
                                <div
                                    key={i}
                                    className="p-3 rounded-xl border border-slate-100 bg-slate-50 flex items-center justify-between"
                                >
                                    <span className="text-xs font-bold text-slate-800">{headline}</span>
                                    <span className="text-[9px] font-black text-primary uppercase">Insight</span>
                                </div>
                            ))}
                            {(!marketResearch || !marketResearch.headlines || marketResearch.headlines.length === 0) && (
                                <div className="text-xs text-slate-400 italic text-center py-4">
                                    No market intelligence available
                                </div>
                            )}
                        </div>
                    </Card>

                    <Card className="p-6 border-slate-100 shadow-sm bg-white">
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">
                            Order Book Depth
                        </h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Bids</p>
                                {(orderBook?.bids || []).slice(0, 5).map((bid, i) => (
                                    <div
                                        key={i}
                                        className="flex justify-between text-xs font-bold text-slate-700 py-1"
                                    >
                                        <span>{formatPrice(bid.price)}</span>
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
                                    <div
                                        key={i}
                                        className="flex justify-between text-xs font-bold text-slate-700 py-1"
                                    >
                                        <span>{formatPrice(ask.price)}</span>
                                        <span>{ask.qty}</span>
                                    </div>
                                ))}
                                {(!orderBook || !orderBook.asks || orderBook.asks.length === 0) && (
                                    <div className="text-xs text-slate-400 italic">No ask data available</div>
                                )}
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6 border-slate-100 shadow-sm bg-white">
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">
                            Exchange Status
                        </h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-slate-600">NSE</span>
                                <span
                                    className={`text-xs font-black px-2 py-0.5 rounded-full ${
                                        exchangeStatus?.nse === 'open'
                                            ? 'bg-green-100 text-green-700'
                                            : 'bg-red-100 text-red-700'
                                    }`}
                                >
                  {exchangeStatus?.nse || 'closed'}
                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-600">BSE</span>
                                <span
                                    className={`text-xs font-black px-2 py-0.5 rounded-full ${
                                        exchangeStatus?.bse === 'open'
                                            ? 'bg-green-100 text-green-700'
                                            : 'bg-red-100 text-red-700'
                                    }`}
                                >
                  {exchangeStatus?.bse || 'closed'}
                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-600">MCX</span>
                                <span
                                    className={`text-xs font-black px-2 py-0.5 rounded-full ${
                                        exchangeStatus?.mcx === 'open'
                                            ? 'bg-green-100 text-green-700'
                                            : 'bg-red-100 text-red-700'
                                    }`}
                                >
                  {exchangeStatus?.mcx || 'closed'}
                </span>
                            </div>
                            <div className="pt-2 border-t border-slate-100">
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-600">System Status</span>
                                    <span className="text-xs font-black px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                    connected
                  </span>
                                </div>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Recent Trades */}
                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">
                        Recent Trades
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                            <tr className="border-b border-slate-100">
                                <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                    Symbol
                                </th>
                                <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                    Side
                                </th>
                                <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                    Quantity
                                </th>
                                <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                    Price
                                </th>
                                <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                    PnL
                                </th>
                                <th className="text-left py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                    Time
                                </th>
                            </tr>
                            </thead>
                            <tbody>
                            {(recentTrades || []).slice(0, 5).map((trade, i) => (
                                <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                                    <td className="py-3 font-black text-slate-900">{trade.symbol}</td>
                                    <td
                                        className={`py-3 font-black ${
                                            trade.action === 'BUY'
                                                ? 'text-green-600'
                                                : trade.action === 'SELL'
                                                    ? 'text-red-500'
                                                    : 'text-slate-500'
                                        }`}
                                    >
                                        {trade.action}
                                    </td>
                                    <td className="py-3 text-slate-700">{trade.quantity}</td>
                                    <td className="py-3 font-black text-slate-900">
                                        {formatPrice(trade.price)}
                                    </td>
                                    <td
                                        className={`py-3 font-black ${
                                            trade.pnl > 0
                                                ? 'text-green-600'
                                                : trade.pnl < 0
                                                    ? 'text-red-500'
                                                    : 'text-slate-500'
                                        }`}
                                    >
                                        {trade.pnl > 0 ? '+' : ''}
                                        {formatPrice(trade.pnl)}
                                    </td>
                                    <td className="py-3 text-[10px] text-slate-500">
                                        {trade.timestamp || trade.created_at
                                            ? new Date(trade.timestamp || trade.created_at).toLocaleTimeString()
                                            : '--'}
                                    </td>
                                </tr>
                            ))}
                            {(!recentTrades || recentTrades.length === 0) && (
                                <tr>
                                    <td colSpan={6} className="py-8 text-center text-slate-400 text-sm">
                                        No recent trades
                                    </td>
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
