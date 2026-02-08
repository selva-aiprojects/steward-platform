import React, { useState, useEffect } from 'react';
import { Card } from "../components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Calendar, TrendingUp, Shield, Activity, Download, Filter, TrendingDown, Target, RefreshCcw, Loader2 } from 'lucide-react';
import { fetchTrades, fetchStrategies, fetchDailyPnL } from "../services/api";
import { useUser } from "../context/UserContext";
import { useAppData } from "../context/AppDataContext";
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Link } from "react-router-dom";

const mockPerformance = [
    { name: 'Mon', user: 4000, agent: 2400 },
    { name: 'Tue', user: 3000, agent: 1398 },
    { name: 'Wed', user: 2000, agent: 9800 },
    { name: 'Thu', user: 2780, agent: 3908 },
    { name: 'Fri', user: 1890, agent: 4800 },
];
const fallbackMovers = [
    { symbol: 'RELIANCE', change: 1.2 },
    { symbol: 'TCS', change: -0.5 },
    { symbol: 'HDFCBANK', change: 0.8 },
    { symbol: 'INFY', change: 0.6 },
    { symbol: 'ICICIBANK', change: -0.3 }
];
const fallbackProjections = [
    { ticker: 'RELIANCE', move_prediction: 'HOLD' },
    { ticker: 'TCS', move_prediction: 'BUY' },
    { ticker: 'INFY', move_prediction: 'HOLD' },
    { ticker: 'HDFCBANK', move_prediction: 'BUY' },
    { ticker: 'ICICIBANK', move_prediction: 'HOLD' }
];
const fallbackWatchlist = [
    { symbol: 'RELIANCE', change: '+0.6%' },
    { symbol: 'TCS', change: '-0.2%' },
    { symbol: 'INFY', change: '+0.4%' },
    { symbol: 'HDFCBANK', change: '+0.3%' },
    { symbol: 'ICICIBANK', change: '-0.1%' }
];

export function Reports() {
    const { user, selectedUser, isAdmin } = useUser();
    const {
        trades: appTrades,
        strategies: appStrategies,
        projections,
        watchlist,
        marketMovers,
        stewardPrediction,
        loading: appLoading
    } = useAppData();

    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState('This Week');
    const [trades, setTrades] = useState([]);
    const [strategies, setStrategies] = useState([]);
    const [dailyPnL, setDailyPnL] = useState([]);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                const userId = selectedUser?.id || user?.id;
                if (!userId) return;

                const [tradesData, strategiesData, dailyPnLData] = await Promise.all([
                    fetchTrades(userId),
                    fetchStrategies(),
                    fetchDailyPnL(userId)
                ]);

                setTrades(tradesData || []);
                setStrategies(strategiesData || []);
                setDailyPnL(dailyPnLData || []);
            } catch (error) {
                console.error('Error loading report data:', error);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [user?.id, selectedUser?.id]); // Changed dependency to only watch IDs to prevent infinite loop

    const refreshAllData = async () => {
        setLoading(true);
        try {
            const userId = selectedUser?.id || user?.id;
            if (!userId) return;

            const [tradesData, strategiesData, dailyPnLData] = await Promise.all([
                fetchTrades(userId),
                fetchStrategies(),
                fetchDailyPnL(userId)
            ]);

            setTrades(tradesData || []);
            setStrategies(strategiesData || []);
            setDailyPnL(dailyPnLData || []);
        } catch (error) {
            console.error('Error refreshing data:', error);
        } finally {
            setLoading(false);
        }
    };

    const generatePDF = () => {
        const doc = new jsPDF();
        doc.setFontSize(22);
        doc.text("StockSteward AI - Executive Performance Report", 14, 22);
        
        // Add more PDF content as needed
        doc.save(`steward-report-${new Date().toISOString().slice(0, 10)}.pdf`);
    };

    if (loading) {
        return (
            <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400">
                <Loader2 className="animate-spin mb-4" size={32} />
                <p className="font-bold uppercase text-[10px] tracking-widest text-[#0A2A4D]">Analyzing execution logs...</p>
            </div>
        );
    }

    return (
        <div data-testid="reports-container" className="pb-4 space-y-8 animate-in fade-in duration-500">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900 font-heading">
                        {user?.role === 'AUDITOR' ? 'Compliance Audit Journal' :
                            user?.role === 'BUSINESS_OWNER' ? 'Executive ROI Ledger' :
                                'Performance Reports'}
                    </h1>
                    <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-[0.3em] leading-none">
                        {user?.role === 'AUDITOR' ? 'System Compliance & Risk Audit' :
                            user?.role === 'BUSINESS_OWNER' ? 'Revenue & Profitability Analysis' :
                                'Trading Performance & Analytics'}
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <button
                        onClick={refreshAllData}
                        disabled={loading}
                        className="bg-white text-slate-900 px-4 py-2 rounded-xl font-bold flex items-center gap-2 border border-slate-200 hover:bg-slate-50 active:scale-95 transition-all"
                    >
                        {loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCcw size={16} />}
                        Refresh
                    </button>
                    <button
                        onClick={generatePDF}
                        disabled={loading}
                        className="bg-primary text-white px-6 py-2 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all"
                    >
                        <Download size={16} />
                        Export PDF
                    </button>
                </div>
            </header>

            {/* Investment Reports Link */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-xl border border-green-200">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-black text-slate-900 mb-2">Investment Performance Analysis</h2>
                        <p className="text-slate-600 mb-4">Compare algorithmic vs manual trading performance with detailed analytics</p>
                    </div>
                    <Link 
                        to="/reports/investment" 
                        className="bg-primary text-white px-6 py-3 rounded-xl font-black hover:opacity-90 transition-all flex items-center gap-2"
                    >
                        <TrendingUp size={18} />
                        View Investment Reports
                    </Link>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-bold text-slate-900 leading-none font-heading">Steward Agent Alpha</h2>
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Performance Curve</p>
                    </div>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart
                                data={dailyPnL.length > 0 ? dailyPnL : mockPerformance}
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
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
                                    formatter={(value) => [`₹${value.toLocaleString()}`, 'P&L']}
                                    contentStyle={{
                                        borderRadius: '12px',
                                        border: 'none',
                                        boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
                                    }}
                                />
                                <Line 
                                    type="monotone" 
                                    dataKey="user" 
                                    stroke="#10b981" 
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#10b981' }}
                                    activeDot={{ r: 6, stroke: '#10b981', strokeWidth: 2, fill: '#fff' }}
                                    name="User Performance"
                                />
                                <Line 
                                    type="monotone" 
                                    dataKey="agent" 
                                    stroke="#3b82f6" 
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#3b82f6' }}
                                    activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2, fill: '#fff' }}
                                    name="Agent Performance"
                                />
                                <defs>
                                    <linearGradient id="colorUser" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.1}/>
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                                    </linearGradient>
                                    <linearGradient id="colorAgent" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-bold text-slate-900 leading-none font-heading">Strategy Engine Performance</h2>
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Volume Distribution</p>
                    </div>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={strategies.length > 0 ? strategies : [
                                    { name: 'SMA Crossover', volume: 4000, win_rate: 78, pnl: 1200 },
                                    { name: 'RSI Mean Rev', volume: 3000, win_rate: 65, pnl: 800 },
                                    { name: 'MACD Signal', volume: 2000, win_rate: 72, pnl: 600 },
                                    { name: 'Bollinger Band', volume: 2780, win_rate: 68, pnl: 900 },
                                    { name: 'Ensemble', volume: 1890, win_rate: 82, pnl: 1500 }
                                ]}
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
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
                                    formatter={(value) => [`₹${value.toLocaleString()}`, 'Volume']}
                                    contentStyle={{
                                        borderRadius: '12px',
                                        border: 'none',
                                        boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
                                    }}
                                />
                                <Bar dataKey="volume" fill="#8884d8" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>

            <Card className="p-6 border-slate-100 shadow-sm bg-white">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-lg font-bold text-slate-900 leading-none font-heading">Strategy Engine Performance</h2>
                    <div className="flex gap-2">
                        <button className="px-3 py-1.5 text-xs font-bold bg-primary text-white rounded-lg">All Engines</button>
                        <button className="px-3 py-1.5 text-xs font-bold bg-slate-100 text-slate-600 rounded-lg">Active Only</button>
                        <button className="px-3 py-1.5 text-xs font-bold bg-slate-100 text-slate-600 rounded-lg">High Volume</button>
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-slate-200">
                                <th className="px-8 py-5 text-left font-bold text-slate-400 text-[10px] uppercase tracking-widest">Strategy Engine</th>
                                <th className="px-8 py-5 text-left font-bold text-slate-400 text-[10px] uppercase tracking-widest">Volume</th>
                                <th className="px-8 py-5 text-left font-bold text-slate-400 text-[10px] uppercase tracking-widest">Win Rate</th>
                                <th className="px-8 py-5 text-left font-bold text-slate-400 text-[10px] uppercase tracking-widest">PnL</th>
                                <th className="px-8 py-5 text-right font-bold text-slate-400 text-[10px] uppercase tracking-widest">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {strategies.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="px-8 py-10 text-center">
                                        <p className="text-slate-400 text-sm">No strategy data available</p>
                                    </td>
                                </tr>
                            ) : (
                                strategies.map((row, i) => (
                                    <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                                        <td className="px-8 py-6">
                                            <div>
                                                <p className="font-bold text-slate-900">{row.name}</p>
                                                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Execution Frequency: {row.frequency || 'HIGH'}</p>
                                            </div>
                                        </td>
                                        <td className="px-8 py-6 font-bold text-slate-600 text-xs">INR {(row.volume || 0).toLocaleString()}</td>
                                        <td className="px-8 py-6 font-black text-green-600 text-xs">{row.win_rate || 0}%</td>
                                        <td className={`px-8 py-6 font-black text-sm ${(row.pnl || 0) >= 0 ? 'text-primary' : 'text-red-500'}`}>
                                            {(row.pnl || 0) >= 0 ? '+' : ''}INR {(row.pnl || 0).toLocaleString()}
                                        </td>
                                        <td className="px-8 py-6 text-right">
                                            <span className={`px-3 py-1 rounded-lg text-[10px] font-black tracking-tighter ${row.status === 'STABLE' ? 'bg-green-50 text-green-700' :
                                                row.status === 'OPTIMIZING' ? 'bg-primary/10 text-primary' : 'bg-orange-50 text-orange-600'
                                                }`}>{row.status || 'OFFLINE'}</span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-slate-900 mb-4">Gainers</h3>
                    <div className="space-y-3">
                        {(marketMovers && marketMovers.length ? marketMovers : fallbackMovers).filter(m => (typeof m.change === 'string' ? parseFloat(m.change) : m.change) >= 0).slice(0, 5).map((m, i) => {
                            const changeValue = typeof m.change === 'string' ? parseFloat(m.change) : (m.change ?? 0);
                            const changeLabel = typeof m.change === 'string' && m.change.toString().includes('%')
                                ? m.change
                                : `${changeValue >= 0 ? '+' : ''}${changeValue}%`;
                            return (
                            <div key={`g-${i}`} className="flex items-center justify-between text-xs font-bold text-slate-700">
                                <span>{m.symbol}</span>
                                <span className="text-green-600">{changeLabel}</span>
                            </div>
                            );
                        })}
                    </div>
                </Card>

                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-slate-900 mb-4">Losers</h3>
                    <div className="space-y-3">
                        {(marketMovers && marketMovers.length ? marketMovers : fallbackMovers).filter(m => (typeof m.change === 'string' ? parseFloat(m.change) : m.change) < 0).slice(0, 5).map((m, i) => {
                            const changeValue = typeof m.change === 'string' ? parseFloat(m.change) : (m.change ?? 0);
                            const changeLabel = typeof m.change === 'string' && m.change.toString().includes('%')
                                ? m.change
                                : `${changeValue >= 0 ? '+' : ''}${changeValue}%`;
                            return (
                            <div key={`l-${i}`} className="flex items-center justify-between text-xs font-bold text-slate-700">
                                <span>{m.symbol}</span>
                                <span className="text-red-600">{changeLabel}</span>
                            </div>
                            );
                        })}
                    </div>
                </Card>

                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-slate-900 mb-4">Tomorrow Outlook</h3>
                    <div className="space-y-3">
                        {(projections && projections.length ? projections : fallbackProjections).slice(0, 5).map((p, i) => (
                            <div key={`p-${i}`} className="flex items-center justify-between text-xs font-bold text-slate-700">
                                <span>{p.ticker}</span>
                                <span className="text-primary">{p.move_prediction}</span>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>

            <div className="space-y-6">
                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-bold uppercase tracking-widest text-slate-900">Steward Prediction</h3>
                        <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Next Session</span>
                    </div>
                    <p className="text-xs font-bold text-slate-700 leading-relaxed">
                        {stewardPrediction?.prediction || 'Market intelligence syncing...'}
                    </p>
                    <div className="mt-3 flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                        <span>Decision: {stewardPrediction?.decision || 'HOLD'}</span>
                        <span>Confidence: {stewardPrediction?.confidence || 0}%</span>
                    </div>
                </Card>

                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-slate-900 mb-4">Watchlist Snapshot</h3>
                    <div className="space-y-3">
                        {(watchlist && watchlist.length ? watchlist : fallbackWatchlist).slice(0, 6).map((w, i) => (
                            <div key={`w-${i}`} className="flex items-center justify-between text-xs font-bold text-slate-700">
                                <span>{w.symbol}</span>
                                <span className="text-slate-500">{w.change || '0.0%'}</span>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
            <div className="space-y-6">
                <h2 className="text-xl font-bold text-slate-900 px-1 font-heading uppercase tracking-widest text-sm">Execution Intelligence Journal</h2>
                <div className="grid grid-cols-1 gap-6">
                    {trades.length === 0 ? (
                        <Card className="p-10 border-slate-100 shadow-sm bg-white text-center">
                            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">No execution logs available</p>
                        </Card>
                    ) : (
                        trades.map((entry) => (
                            <Card key={entry.id} className="p-0 border-slate-100 shadow-sm overflow-hidden bg-white">
                                <div className="flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-slate-50">
                                    <div className="p-6 md:w-48 bg-slate-50/50">
                                        <div className="flex items-center justify-between mb-4">
                                            <span className="text-[10px] font-bold text-slate-400">
                                                {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                            <span className="text-[10px] font-bold text-primary">TX-{entry.id}</span>
                                        </div>
                                        <h3 className="text-2xl font-bold text-slate-900">{entry.symbol}</h3>
                                        <span className={`inline-block mt-2 px-3 py-1 rounded-lg text-[10px] font-bold tracking-widest ${entry.action === 'BUY' ? 'bg-green-500 text-white' :
                                            entry.action === 'SELL' ? 'bg-red-500 text-white' : 'bg-slate-200 text-slate-600'
                                            }`}>{entry.action}</span>
                                    </div>

                                    <div className="p-6 flex-1 grid grid-cols-1 md:grid-cols-2 gap-8">
                                        <div>
                                            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-2">Market Behavior Snapshot</p>
                                            <p className="text-xs font-bold text-slate-700 leading-relaxed italic border-l-2 border-primary pl-3">
                                                "{entry.market_behavior}"
                                            </p>
                                            <div className="mt-4">
                                                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">Entry/Snapshot Price</p>
                                                <p className="text-sm font-bold text-slate-900">INR {entry.price}</p>
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-2">Algo Smart Decision Logic</p>
                                            <p className="text-xs font-medium text-slate-600 leading-relaxed">
                                                {entry.decision_logic}
                                            </p>
                                            <div className="mt-4 flex items-center justify-between">
                                                <div>
                                                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">Session Outcome</p>
                                                    <p className={`text-sm font-bold ${entry.pnl?.startsWith('+') ? 'text-primary' : 'text-slate-900'}`}>{entry.pnl}</p>
                                                </div>
                                                <button className="text-[10px] font-bold text-slate-400 hover:text-primary transition-colors cursor-pointer uppercase tracking-widest bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">Audit Deep-Link</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </Card>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}