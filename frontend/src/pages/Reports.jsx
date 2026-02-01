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
                <Card className="p-6 border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                            <TrendingUp size={20} />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-slate-900 leading-none">My Performance Report</h2>
                            <p className="text-xs text-slate-500 mt-1">Direct User executions and manual rebalancing</p>
                        </div>
                    </div>
                    <div className="h-64 mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={mockPerformance}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                />
                                <Bar dataKey="user" fill="#2DBD42" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                {/* Agent Report */}
                <Card className="p-6 border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-green-50 rounded-lg text-green-600">
                            <Shield size={20} />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-slate-900 leading-none">Steward Agent Report</h2>
                            <p className="text-xs text-slate-500 mt-1">Autonomous strategy execution summary</p>
                        </div>
                    </div>
                    <div className="h-64 mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={mockPerformance}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                />
                                <Line type="monotone" dataKey="agent" stroke="#0A2A4D" strokeWidth={3} dot={{ r: 4, fill: '#0A2A4D' }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>

            <Card className="p-0 border-slate-200 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <div className="flex items-center gap-2">
                        <Activity size={18} className="text-primary" />
                        <h3 className="font-bold text-slate-900">Algo Trading Summary</h3>
                    </div>
                    <span className="text-[10px] font-bold bg-green-500 text-white px-2 py-0.5 rounded uppercase">Live Ledger</span>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-slate-500 font-bold bg-white border-b">
                            <tr>
                                <th className="px-6 py-4">STRATEGY</th>
                                <th className="px-6 py-4">TOTAL TRADES</th>
                                <th className="px-6 py-4">WIN RATE</th>
                                <th className="px-6 py-4">DAILY PNL</th>
                                <th className="px-6 py-4 text-right">STATUS</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {[
                                { name: 'Mean Reversion v4', trades: 12, win: '68%', pnl: '+$1,240', status: 'ACTIVE' },
                                { name: 'Trend Follower Llama', trades: 4, win: '92%', pnl: '+$5,800', status: 'ACTIVE' },
                                { name: 'Sentiment Alpha v1', trades: 0, win: '0%', pnl: '$0', status: 'IDLE' },
                            ].map((row, i) => (
                                <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                                    <td className="px-6 py-4 font-bold text-slate-900">{row.name}</td>
                                    <td className="px-6 py-4 font-medium">{row.trades}</td>
                                    <td className="px-6 py-4 font-medium text-green-600">{row.win}</td>
                                    <td className="px-6 py-4 font-bold text-primary">{row.pnl}</td>
                                    <td className="px-6 py-4 text-right">
                                        <span className={`px-2 py-1 rounded text-[10px] font-black ${row.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'
                                            }`}>{row.status}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
