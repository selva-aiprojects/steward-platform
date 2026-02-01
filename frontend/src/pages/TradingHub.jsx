import React, { useState } from 'react';
import { Card } from "../components/ui/card";
import { Play, Pause, RefreshCcw, Zap, Target, TrendingUp } from 'lucide-react';

export function TradingHub() {
    const [strategies, setStrategies] = useState([
        { id: 1, name: 'Llama-3 Trend Scalper', symbol: 'NVDA', status: 'RUNNING', pnl: '+4.2%' },
        { id: 2, name: 'MACD Mean Reversion', symbol: 'TSLA', status: 'PAUSED', pnl: '-1.1%' },
        { id: 3, name: 'Sentiment Arbitrage', symbol: 'BTC/USD', status: 'IDLE', pnl: '0.0%' },
    ]);

    return (
        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
            <header className="flex justify-between items-center bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900 font-heading">Trading Hub</h1>
                    <p className="text-slate-500 mt-1 uppercase text-[10px] font-bold tracking-widest leading-none flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                        Algo Engine: Online & Monitoring 14 Parallel Threads
                    </p>
                </div>
                <button className="bg-primary text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:opacity-90 transition-all shadow-lg shadow-primary/20">
                    <Zap size={18} fill="currentColor" />
                    Launch New Strategy
                </button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { label: 'Total Algorithmic Volume', value: '$1.2M', icon: RefreshCcw, color: 'text-indigo-600' },
                    { label: 'Active Positions', value: '8', icon: Target, color: 'text-green-600' },
                    { label: 'Avg Daily Alpha', value: '2.4%', icon: TrendingUp, color: 'text-primary' },
                ].map((stat, i) => (
                    <Card key={i} className="p-6 border-slate-200 shadow-sm flex items-center justify-between">
                        <div>
                            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none mb-2">{stat.label}</p>
                            <h3 className="text-2xl font-bold text-slate-900">{stat.value}</h3>
                        </div>
                        <div className={`p-3 bg-slate-50 rounded-xl ${stat.color}`}>
                            <stat.icon size={22} />
                        </div>
                    </Card>
                ))}
            </div>

            <div className="space-y-4">
                <h2 className="text-xl font-bold text-slate-900 px-1">Active Automated Strategies</h2>
                <div className="grid grid-cols-1 gap-4">
                    {strategies.map((strat) => (
                        <Card key={strat.id} className="p-6 border-slate-200 shadow-sm hover:border-primary/30 transition-all group">
                            <div className="flex flex-wrap items-center justify-between gap-6">
                                <div className="flex items-center gap-4">
                                    <div className={`h-12 w-12 rounded-2xl flex items-center justify-center font-black text-white ${strat.status === 'RUNNING' ? 'bg-green-500' : 'bg-slate-300'
                                        }`}>
                                        {strat.symbol.substring(0, 2)}
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-slate-900">{strat.name}</h3>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="text-xs font-bold text-slate-500">{strat.symbol}</span>
                                            <span className="h-1 w-1 rounded-full bg-slate-300" />
                                            <span className={`text-[10px] font-black ${strat.status === 'RUNNING' ? 'text-green-600' : 'text-slate-400'
                                                }`}>{strat.status}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex-1 grid grid-cols-3 gap-4 border-l border-r px-8 border-slate-100">
                                    <div>
                                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Session Profit</p>
                                        <p className={`text-sm font-bold ${strat.pnl.startsWith('+') ? 'text-green-600' : 'text-slate-900'}`}>{strat.pnl}</p>
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Drawdown</p>
                                        <p className="text-sm font-bold text-slate-900">1.2%</p>
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Execution Mode</p>
                                        <p className="text-sm font-bold text-slate-900">Auto-Optimizing</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    {strat.status === 'RUNNING' ? (
                                        <button className="p-2 text-slate-400 hover:text-orange-500 hover:bg-orange-50 rounded-lg transition-colors">
                                            <Pause size={20} />
                                        </button>
                                    ) : (
                                        <button className="p-2 text-slate-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors">
                                            <Play size={20} />
                                        </button>
                                    )}
                                    <button className="px-4 py-2 rounded-lg bg-slate-100 text-slate-600 font-bold text-xs hover:bg-slate-200">
                                        Configuration
                                    </button>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>

            <Card className="p-8 bg-slate-900 text-white border-none shadow-2xl overflow-hidden relative">
                <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="max-w-md">
                        <div className="flex items-center gap-2 mb-4">
                            <span className="px-2 py-0.5 rounded bg-blue-500 text-[10px] font-black uppercase tracking-widest">Global Watcher</span>
                            <span className="text-blue-400 text-xs font-bold leading-none">Agent ID: SS-88-ALPHA</span>
                        </div>
                        <h3 className="text-2xl font-bold mb-3 font-heading">Steward AI is monitoring 480 market triggers.</h3>
                        <p className="text-slate-400 text-sm leading-relaxed mb-6">
                            Autonomous trading is active for the next market session. Your risk settings permit up to **$25,000** exposure per trade with a **-2%** hard stop.
                        </p>
                        <div className="flex gap-4">
                            <button className="px-6 py-2 bg-white text-slate-900 rounded-xl font-black text-xs hover:scale-105 transition-transform">Emergency Stop All</button>
                            <button className="px-6 py-2 bg-white/10 text-white rounded-xl font-bold text-xs border border-white/20 hover:bg-white/20 transition-colors">View Logic Tree</button>
                        </div>
                    </div>
                </div>
                {/* Visual accents */}
                <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-primary/20 to-transparent pointer-events-none" />
            </Card>
        </div>
    );
}
