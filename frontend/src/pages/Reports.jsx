import React, { useState } from 'react';
import { Card } from "../components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Calendar, TrendingUp, Shield, Activity } from 'lucide-react';

const mockPerformance = [
    { name: 'Mon', user: 4000, agent: 2400 },
    { name: 'Tue', user: 3000, agent: 1398 },
    { name: 'Wed', user: 2000, agent: 9800 },
    { name: 'Thu', user: 2780, agent: 3908 },
    { name: 'Fri', user: 1890, agent: 4800 },
];

export function Reports() {
    const [timeframe, setTimeframe] = useState('Daily');

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900 font-heading">Performance Reports</h1>
                    <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none">System Analytics & Audit</p>
                </div>
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
                            <p className="text-2xl font-black text-slate-900">$18.4K</p>
                            <p className="text-[10px] text-green-600 font-black uppercase tracking-tighter">+12.4% THIS PERIOD</p>
                        </div>
                    </div>
                    <div className="h-64 mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={mockPerformance}>
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
                            <p className="text-2xl font-black text-slate-900">$64.2K</p>
                            <p className="text-[10px] text-primary font-black uppercase tracking-tighter">+24.8% THIS PERIOD</p>
                        </div>
                    </div>
                    <div className="h-64 mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={mockPerformance}>
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

            <Card className="p-0 border-slate-100 shadow-sm overflow-hidden bg-white">
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
                            {[
                                { name: 'Alpha Mean Reversion v4', trades: '$2.4M', win: '68.4%', pnl: '+$12,450', status: 'STABLE' },
                                { name: 'Groq Llama-3 Scalper', trades: '$840K', win: '92.1%', pnl: '+$5,800', status: 'OPTIMIZING' },
                                { name: 'Sentiment Arbitrage v1.2', trades: '$120K', win: '44.8%', pnl: '-$420', status: 'RE-CALIBRATING' },
                            ].map((row, i) => (
                                <tr key={i} className="hover:bg-slate-50 transition-colors group cursor-pointer">
                                    <td className="px-8 py-6">
                                        <p className="font-black text-slate-900">{row.name}</p>
                                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Execution Frequency: HIGH</p>
                                    </td>
                                    <td className="px-8 py-6 font-bold text-slate-600 text-xs">{row.trades}</td>
                                    <td className="px-8 py-6 font-black text-green-600 text-xs">{row.win}</td>
                                    <td className={`px-8 py-6 font-black text-sm ${row.pnl.startsWith('+') ? 'text-primary' : 'text-red-500'}`}>
                                        {row.pnl}
                                    </td>
                                    <td className="px-8 py-6 text-right">
                                        <span className={`px-3 py-1 rounded-lg text-[10px] font-black tracking-tighter ${row.status === 'STABLE' ? 'bg-green-50 text-green-700' :
                                            row.status === 'OPTIMIZING' ? 'bg-primary/10 text-primary' : 'bg-orange-50 text-orange-600'
                                            }`}>{row.status}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
            <div className="space-y-6">
                <h2 className="text-xl font-black text-slate-900 px-1 font-heading uppercase tracking-widest text-sm">Execution Intelligence Journal</h2>
                <div className="grid grid-cols-1 gap-6">
                    {[
                        {
                            id: 'TX-4829',
                            ticker: 'NVDA',
                            action: 'BUY',
                            snapshot: '$782.10',
                            behavior: 'Breakout above V-WAP with high relative volume on 5-min candle.',
                            decision: 'Algo detected institutional accumulation. Leveraged 1.2x on high-confidence breakout signal.',
                            pnl: '+2.41%',
                            time: '09:42 AM'
                        },
                        {
                            id: 'TX-4835',
                            ticker: 'TSLA',
                            action: 'SELL',
                            snapshot: '$194.50',
                            behavior: 'Double top formation at resistance. RSI showing bearish divergence.',
                            decision: 'Risk engine triggered hard exit to preserve alpha. Sentiment index dropped to 32/100.',
                            pnl: '+1.10%',
                            time: '11:15 AM'
                        },
                        {
                            id: 'TX-4842',
                            ticker: 'AAPL',
                            action: 'HOLD',
                            snapshot: '$188.90',
                            behavior: 'Sideways consolidation. No clear direction in order flow.',
                            decision: 'Strategy "Trend Follower" stayed neutral to avoid wash-trades during low volatility.',
                            pnl: '0.00%',
                            time: '02:30 PM'
                        },
                    ].map((entry) => (
                        <Card key={entry.id} className="p-0 border-slate-100 shadow-sm overflow-hidden bg-white">
                            <div className="flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-slate-50">
                                <div className="p-6 md:w-48 bg-slate-50/50">
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="text-[10px] font-black text-slate-400">{entry.time}</span>
                                        <span className="text-[10px] font-black text-primary">{entry.id}</span>
                                    </div>
                                    <h3 className="text-2xl font-black text-slate-900">{entry.ticker}</h3>
                                    <span className={`inline-block mt-2 px-3 py-1 rounded-lg text-[10px] font-black tracking-widest ${entry.action === 'BUY' ? 'bg-green-500 text-white' :
                                            entry.action === 'SELL' ? 'bg-red-500 text-white' : 'bg-slate-200 text-slate-600'
                                        }`}>{entry.action}</span>
                                </div>

                                <div className="p-6 flex-1 grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div>
                                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-2">Market Behavior Snapshot</p>
                                        <p className="text-xs font-bold text-slate-700 leading-relaxed italic border-l-2 border-primary pl-3">
                                            "{entry.behavior}"
                                        </p>
                                        <div className="mt-4">
                                            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Entry/Snapshot Price</p>
                                            <p className="text-sm font-black text-slate-900">{entry.snapshot}</p>
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-2">Algo Smart Decision Logic</p>
                                        <p className="text-xs font-medium text-slate-600 leading-relaxed">
                                            {entry.decision}
                                        </p>
                                        <div className="mt-4 flex items-center justify-between">
                                            <div>
                                                <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Session Outcome</p>
                                                <p className={`text-sm font-black ${entry.pnl.startsWith('+') ? 'text-primary' : 'text-slate-900'}`}>{entry.pnl}</p>
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
