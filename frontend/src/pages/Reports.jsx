import React, { useState, useEffect } from 'react';
import { Card } from "../components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Calendar, TrendingUp, Shield, Activity, Download, Filter, TrendingDown, Target, RefreshCcw, Loader2 } from 'lucide-react';
import { fetchTrades, fetchStrategies, fetchDailyPnL } from "../services/api";
import { useUser } from "../context/UserContext";
import { useAppData } from "../context/AppDataContext";
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const mockPerformance = [
    { name: 'Mon', user: 4000, agent: 2400 },
    { name: 'Tue', user: 3000, agent: 1398 },
    { name: 'Wed', user: 2000, agent: 9800 },
    { name: 'Thu', user: 2780, agent: 3908 },
    { name: 'Fri', user: 1890, agent: 4800 },
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

    const [timeframe, setTimeframe] = useState('Daily');
    const [trades, setTrades] = useState([]);
    const [performance, setPerformance] = useState([]);
    const [strategies, setStrategies] = useState([]);
    const [loading, setLoading] = useState(true);

    const viewId = selectedUser?.id || (isAdmin ? null : user?.id);

    useEffect(() => {
        if (appTrades) {
            setTrades(appTrades.filter(t => t.decision_logic));
        }
    }, [appTrades]);

    useEffect(() => {
        if (appStrategies) {
            setStrategies(appStrategies);
        }
    }, [appStrategies]);

    useEffect(() => {
        const loadPnL = async () => {
            setLoading(true);
            try {
                const dailyPnL = await fetchDailyPnL(viewId);
                setPerformance(dailyPnL.length > 0 ? dailyPnL : [
                    { name: 'Mon', user: 0, agent: 0 },
                    { name: 'Tue', user: 0, agent: 0 },
                    { name: 'Wed', user: 0, agent: 0 },
                    { name: 'Thu', user: 0, agent: 0 },
                    { name: 'Fri', user: 0, agent: 0 },
                ]);
            } catch (err) {
                console.error("PnL Fetch Error:", err);
            } finally {
                setLoading(false);
            }
        };
        loadPnL();
    }, [viewId]);

    const downloadReport = () => {
        const doc = new jsPDF();

        // Header
        doc.setFontSize(20);
        doc.text("StockSteward AI - Executive Performance Report", 14, 22);

        doc.setFontSize(10);
        doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);
        doc.text(`Period: ${timeframe}`, 14, 35);

        // Section 1: Algorithmic Summary
        doc.setFontSize(14);
        doc.text("Algorithmic Trading Ledger", 14, 50);

        const algoData = strategies.map(s => [
            s.name,
            `? ${(s.volume || 0).toLocaleString()}`,
            `${s.win_rate || 0}%`,
            `${(s.pnl || 0) >= 0 ? '+' : ''}${(s.pnl || 0).toLocaleString()}`,
            s.status || 'OFFLINE'
        ]);

        autoTable(doc, {
            startY: 55,
            head: [['Strategy Engine', 'Volume', 'Avg Win Rate', 'Period PnL', 'Status']],
            body: algoData,
            theme: 'grid',
            headStyles: { fillColor: [10, 42, 77] }, // #0A2A4D
        });

        // Section 2: Execution Journal
        // Retrieve finalY from the doc object which autoTable updates
        let finalY = (doc.lastAutoTable && doc.lastAutoTable.finalY) || 60;
        finalY += 20;

        doc.setFontSize(14);
        doc.text("Execution Intelligence Journal", 14, finalY);

        const journalData = trades.map(t => [
            new Date(t.timestamp).toLocaleTimeString(),
            t.symbol,
            t.action,
            `? ${t.price}`,
            t.decision_logic.substring(0, 50) + '...'
        ]);

        autoTable(doc, {
            startY: finalY + 5,
            head: [['Time', 'Symbol', 'Action', 'Price', 'Logic Snapshot']],
            body: journalData,
            theme: 'striped',
            headStyles: { fillColor: [45, 189, 66] }, // Primary Green
        });

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
                    <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none">
                        {user?.role === 'AUDITOR' ? 'Algorithmic Execution Integrity Audit' :
                            user?.role === 'BUSINESS_OWNER' ? 'Revenue & Performance Metrics' :
                                'System Analytics & Audit'}
                    </p>
                </div>
                <div className="flex gap-4">
                    <button
                        data-testid="export-pdf-button"
                        onClick={downloadReport}
                        className="flex items-center gap-2 bg-[#0A2A4D] text-white px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest hover:opacity-90 transition-all shadow-lg shadow-indigo-900/20"
                    >
                        <Download size={16} />
                        Export PDF
                    </button>
                    <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200">
                        {['Daily', 'Weekly', 'Yearly'].map((t) => (
                            <button
                                key={t}
                                onClick={() => setTimeframe(t)}
                                className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${timeframe === t ? 'bg-white shadow-sm text-primary' : 'text-slate-500 hover:text-slate-800'
                                    }`}
                            >
                                {t}
                            </button>
                        ))}
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* My Report */}
                <Card className="p-8 border-slate-100 shadow-sm hover:shadow-xl transition-all bg-white overflow-hidden group">
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-slate-50 rounded-xl text-primary transition-colors group-hover:bg-primary group-hover:text-white">
                                <TrendingUp size={20} />
                            </div>
                            <div>
                                <h2 className="text-lg font-black text-slate-900 leading-none font-heading">User Performance</h2>
                                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">Manual Executions Summary</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-2xl font-black text-slate-900">? 18.4K</p>
                            <p className="text-[10px] text-green-600 font-black uppercase tracking-tighter">+12.4% THIS PERIOD</p>
                        </div>
                    </div>
                    <div className="h-64 mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={performance}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} />
                                <Tooltip
                                    cursor={{ fill: '#f8fafc' }}
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)', padding: '12px' }}
                                />
                                <Bar dataKey="user" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} barSize={32} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                {/* Agent Report */}
                <Card className="p-8 border-slate-100 shadow-sm hover:shadow-xl transition-all bg-white overflow-hidden group">
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-slate-50 rounded-xl text-indigo-600 transition-colors group-hover:bg-indigo-600 group-hover:text-white">
                                <Shield size={20} />
                            </div>
                            <div>
                                <h2 className="text-lg font-black text-slate-900 leading-none font-heading">Steward Agent Alpha</h2>
                                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">Autonomous Strategy Audit</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-2xl font-black text-slate-900">? 64.2K</p>
                            <p className="text-[10px] text-primary font-black uppercase tracking-tighter">+24.8% THIS PERIOD</p>
                        </div>
                    </div>
                    <div className="h-64 mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={performance}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8', fontWeight: 700 }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)', padding: '12px' }}
                                />
                                <Line type="monotone" dataKey="agent" stroke="#0A2A4D" strokeWidth={4} dot={{ r: 4, fill: '#0A2A4D', strokeWidth: 2, stroke: '#fff' }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>

            <Card data-testid="algo-trading-ledger" className="p-0 border-slate-100 shadow-sm overflow-hidden bg-white">
                <div className="p-6 border-b border-slate-50 flex justify-between items-center bg-slate-50/30">
                    <div className="flex items-center gap-2">
                        <Activity size={16} className="text-primary" />
                        <h3 className="font-black text-slate-900 text-sm uppercase tracking-wider">Algo Trading Ledger Summary</h3>
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Auto-Updating</span>
                        <span className="text-[10px] font-black bg-primary text-white px-2.5 py-1 rounded-full uppercase tracking-tighter">Live Status</span>
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] bg-white border-b">
                            <tr>
                                <th className="px-8 py-5">STRATEGY ENGINE</th>
                                <th className="px-8 py-5">TOTAL VOLUME</th>
                                <th className="px-8 py-5">AVG WIN RATE</th>
                                <th className="px-8 py-5">PERIOD PNL</th>
                                <th className="px-8 py-5 text-right">SYSTEM STATE</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {strategies.map((row, i) => (
                                <tr key={i} className="hover:bg-slate-50 transition-colors group cursor-pointer">
                                    <td className="px-8 py-6">
                                        <p className="font-black text-slate-900">{row.name}</p>
                                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Execution Frequency: {row.frequency || 'HIGH'}</p>
                                    </td>
                                    <td className="px-8 py-6 font-bold text-slate-600 text-xs">? {(row.volume || 0).toLocaleString()}</td>
                                    <td className="px-8 py-6 font-black text-green-600 text-xs">{row.win_rate || 0}%</td>
                                    <td className={`px-8 py-6 font-black text-sm ${(row.pnl || 0) >= 0 ? 'text-primary' : 'text-red-500'}`}>
                                        {(row.pnl || 0) >= 0 ? '+' : ''}? {(row.pnl || 0).toLocaleString()}
                                    </td>
                                    <td className="px-8 py-6 text-right">
                                        <span className={`px-3 py-1 rounded-lg text-[10px] font-black tracking-tighter ${row.status === 'STABLE' ? 'bg-green-50 text-green-700' :
                                            row.status === 'OPTIMIZING' ? 'bg-primary/10 text-primary' : 'bg-orange-50 text-orange-600'
                                            }`}>{row.status || 'OFFLINE'}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Gainers</h3>
                    <div className="space-y-3">
                        {(marketMovers || []).filter(m => (typeof m.change === 'string' ? parseFloat(m.change) : m.change) >= 0).slice(0, 5).map((m, i) => {
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
                    <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Losers</h3>
                    <div className="space-y-3">
                        {(marketMovers || []).filter(m => (typeof m.change === 'string' ? parseFloat(m.change) : m.change) < 0).slice(0, 5).map((m, i) => {
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
                    <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Tomorrow Outlook</h3>
                    <div className="space-y-3">
                        {(projections || []).slice(0, 5).map((p, i) => (
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
                        <h3 className="text-sm font-black uppercase tracking-widest text-slate-900">Steward Prediction</h3>
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Next Session</span>
                    </div>
                    <p className="text-xs font-bold text-slate-700 leading-relaxed">
                        {stewardPrediction?.prediction || 'Market intelligence syncing...'}
                    </p>
                    <div className="mt-3 flex items-center gap-3 text-[10px] font-black uppercase tracking-widest text-slate-500">
                        <span>Decision: {stewardPrediction?.decision || 'HOLD'}</span>
                        <span>Confidence: {stewardPrediction?.confidence || 0}%</span>
                    </div>
                </Card>

                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-4">Watchlist Snapshot</h3>
                    <div className="space-y-3">
                        {(watchlist || []).slice(0, 6).map((w, i) => (
                            <div key={`w-${i}`} className="flex items-center justify-between text-xs font-bold text-slate-700">
                                <span>{w.symbol}</span>
                                <span className="text-slate-500">{w.change || '0.0%'}</span>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
            <div className="space-y-6">
                <h2 className="text-xl font-black text-slate-900 px-1 font-heading uppercase tracking-widest text-sm">Execution Intelligence Journal</h2>
                <div className="grid grid-cols-1 gap-6">
                    {trades.map((entry) => (
                        <Card key={entry.id} className="p-0 border-slate-100 shadow-sm overflow-hidden bg-white">
                            <div className="flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-slate-50">
                                <div className="p-6 md:w-48 bg-slate-50/50">
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="text-[10px] font-black text-slate-400">
                                            {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                        <span className="text-[10px] font-black text-primary">TX-{entry.id}</span>
                                    </div>
                                    <h3 className="text-2xl font-black text-slate-900">{entry.symbol}</h3>
                                    <span className={`inline-block mt-2 px-3 py-1 rounded-lg text-[10px] font-black tracking-widest ${entry.action === 'BUY' ? 'bg-green-500 text-white' :
                                        entry.action === 'SELL' ? 'bg-red-500 text-white' : 'bg-slate-200 text-slate-600'
                                        }`}>{entry.action}</span>
                                </div>

                                <div className="p-6 flex-1 grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div>
                                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-2">Market Behavior Snapshot</p>
                                        <p className="text-xs font-bold text-slate-700 leading-relaxed italic border-l-2 border-primary pl-3">
                                            "{entry.market_behavior}"
                                        </p>
                                        <div className="mt-4">
                                            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Entry/Snapshot Price</p>
                                            <p className="text-sm font-black text-slate-900">? {entry.price}</p>
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-2">Algo Smart Decision Logic</p>
                                        <p className="text-xs font-medium text-slate-600 leading-relaxed">
                                            {entry.decision_logic}
                                        </p>
                                        <div className="mt-4 flex items-center justify-between">
                                            <div>
                                                <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Session Outcome</p>
                                                <p className={`text-sm font-black ${entry.pnl?.startsWith('+') ? 'text-primary' : 'text-slate-900'}`}>{entry.pnl}</p>
                                            </div>
                                            <button className="text-[10px] font-black text-slate-400 hover:text-primary transition-colors cursor-pointer uppercase tracking-widest bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">Audit Deep-Link</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
}







