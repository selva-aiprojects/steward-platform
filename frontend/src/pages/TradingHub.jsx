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

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Active Automated Strategies */}
                <div className="lg:col-span-8 space-y-6">
                    <h2 className="text-xl font-black text-slate-900 px-1 font-heading uppercase tracking-widest text-sm">Active Automated Strategies</h2>
                    <div className="grid grid-cols-1 gap-4">
                        {strategies.map((strat) => (
                            <Card key={strat.id} className="p-6 border-slate-100 shadow-sm hover:border-primary/30 transition-all group bg-white">
                                <div className="flex flex-wrap items-center justify-between gap-6">
                                    <div className="flex items-center gap-4">
                                        <div className={`h-12 w-12 rounded-2xl flex items-center justify-center font-black text-white ${strat.status === 'RUNNING' ? 'bg-primary' : 'bg-slate-300'
                                            }`}>
                                            {strat.symbol.substring(0, 2)}
                                        </div>
                                        <div>
                                            <h3 className="font-black text-slate-900 leading-none">{strat.name}</h3>
                                            <div className="flex items-center gap-2 mt-2">
                                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{strat.symbol}</span>
                                                <span className="h-1 w-1 rounded-full bg-slate-200" />
                                                <span className={`text-[10px] font-black uppercase ${strat.status === 'RUNNING' ? 'text-green-500' : 'text-slate-400'
                                                    }`}>{strat.status}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4 border-l border-r px-8 border-slate-50">
                                        <div>
                                            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Profitability</p>
                                            <p className={`text-sm font-black ${strat.pnl.startsWith('+') ? 'text-primary' : 'text-slate-900'}`}>{strat.pnl}</p>
                                        </div>
                                        <div className="hidden md:block">
                                            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Drawdown</p>
                                            <p className="text-sm font-black text-slate-900">1.2%</p>
                                        </div>
                                        <div>
                                            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">State</p>
                                            <p className="text-sm font-black text-slate-500 uppercase text-[10px]">Optimizing</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        {strat.status === 'RUNNING' ? (
                                            <button className="p-2.5 bg-slate-50 text-slate-400 hover:text-orange-500 hover:bg-orange-50 rounded-xl transition-all">
                                                <Pause size={18} />
                                            </button>
                                        ) : (
                                            <button className="p-2.5 bg-slate-50 text-slate-400 hover:text-primary hover:bg-green-50 rounded-xl transition-all">
                                                <Play size={18} />
                                            </button>
                                        )}
                                        <button className="px-5 py-2.5 rounded-xl bg-slate-900 text-white font-black text-[10px] uppercase tracking-widest hover:bg-primary transition-all">
                                            CFG
                                        </button>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                </div>

                {/* AI Next Day Projections */}
                <div className="lg:col-span-4 space-y-6">
                    <h2 className="text-xl font-black text-slate-900 px-1 font-heading uppercase tracking-widest text-sm">Next-Day Projections</h2>
                    <Card className="p-6 border-primary/20 bg-green-50/30 shadow-xl shadow-primary/5">
                        <div className="flex items-center gap-2 mb-6">
                            <TrendingUp size={18} className="text-primary" />
                            <span className="text-[10px] font-black text-primary uppercase tracking-[0.2em]">Alpha Recommendation</span>
                        </div>

                        <div className="space-y-4">
                            {[
                                { ticker: 'NVDA', move: '+3.8%', action: 'ACCUMULATE', logic: 'Post-earnings momentum continuation' },
                                { ticker: 'AAPL', move: '-1.2%', action: 'TRIM', logic: 'Resistance at $195 with volume decay' },
                                { ticker: 'TSLA', move: '+5.4%', action: 'BUY', logic: 'FSD V12 rollout hype cycle' },
                            ].map((proj, i) => (
                                <div key={i} className="p-4 rounded-2xl bg-white border border-slate-100 shadow-sm group hover:border-primary/50 transition-all cursor-pointer">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-black text-slate-900">{proj.ticker}</span>
                                        <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${proj.move.startsWith('+') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                            }`}>{proj.move}</span>
                                    </div>
                                    <p className="text-[10px] text-slate-500 font-bold leading-relaxed">{proj.logic}</p>
                                    <div className="mt-3 flex items-center justify-between">
                                        <span className="text-[9px] font-black bg-slate-900 text-white px-2 py-0.5 rounded-md">{proj.action}</span>
                                        <ArrowUpRight size={14} className="text-slate-300 group-hover:text-primary transition-colors" />
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-6 p-4 rounded-2xl bg-slate-900 text-white border-none">
                            <h4 className="text-xs font-black uppercase tracking-widest mb-2 flex items-center gap-2">
                                <Shield size={14} className="text-primary" />
                                Logic Validation
                            </h4>
                            <p className="text-[9px] text-slate-400 font-medium leading-relaxed">
                                Recommendations are based on 14-day trailing sentiment analysis and real-time order flow data.
                                <span className="text-primary font-black ml-1">Live data feed active.</span>
                            </p>
                        </div>
                    </Card>
                </div>
            </div>

            <Card className="p-10 bg-[#0A2A4D] text-white border-none shadow-2xl overflow-hidden relative">
                <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="max-w-xl">
                        <div className="flex items-center gap-2 mb-6">
                            <span className="px-3 py-1 rounded-full bg-primary text-[10px] font-black uppercase tracking-widest">Global Watcher Alpha</span>
                            <span className="text-white/40 text-[10px] font-bold leading-none uppercase tracking-widest">Cluster Node: US-EAST-1</span>
                        </div>
                        <h3 className="text-3xl font-black mb-4 font-heading leading-tight">Steward AI is currently monitoring 842 market triggers.</h3>
                        <p className="text-slate-300 text-sm leading-relaxed mb-8 font-medium">
                            The engine has detected a Bullish Divergence across the Mag-7 complex. Asset allocation is being shifted from **Fixed Income** to **High-Growth Equity** automatically. Emergency stop-loss threshold is fixed at **-2.5%** net portfolio value.
                        </p>
                        <div className="flex flex-wrap gap-4">
                            <button className="px-8 py-3 bg-white text-slate-900 rounded-xl font-black text-xs hover:scale-105 transition-transform uppercase tracking-widest shadow-lg">Emergency Stop All</button>
                            <button className="px-8 py-3 bg-white/10 text-white rounded-xl font-black text-xs border border-white/20 hover:bg-white/20 transition-all uppercase tracking-widest">View Decision Tree</button>
                        </div>
                    </div>

                    <div className="hidden lg:grid grid-cols-2 gap-4 flex-shrink-0">
                        <div className="p-6 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
                            <p className="text-[10px] text-white/40 font-black uppercase tracking-widest mb-1">HFT Latency</p>
                            <p className="text-2xl font-black text-white">42ms</p>
                        </div>
                        <div className="p-6 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
                            <p className="text-[10px] text-white/40 font-black uppercase tracking-widest mb-1">Confidence</p>
                            <p className="text-2xl font-black text-green-400">92%</p>
                        </div>
                    </div>
                </div>
                {/* Visual accents */}
                <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-primary/10 to-transparent pointer-events-none" />
                <div className="absolute -bottom-24 -right-24 h-64 w-64 bg-primary/20 rounded-full blur-[100px] pointer-events-none" />
            </Card>
        </div>
    );
}
