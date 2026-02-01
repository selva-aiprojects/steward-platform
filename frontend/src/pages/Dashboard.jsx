import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from "../components/ui/card" // Mock card for now, or just use div

const data = [
    { name: 'Jan', value: 100000 },
    { name: 'Feb', value: 102000 },
    { name: 'Mar', value: 101500 },
    { name: 'Apr', value: 105000 },
    { name: 'May', value: 108000 },
    { name: 'Jun', value: 112000 },
];

const activityItems = [
    { id: 1, action: "Bought AAPL", strategy: "SMACrossover", pnl: "+$250.00" },
    { id: 2, action: "Sold TSLA", strategy: "RSI Reversal", pnl: "+$120.50" },
    { id: 3, action: "Bought MSFT", strategy: "Momentum", pnl: "-$45.00" },
    { id: 4, action: "Bought GOOGL", strategy: "MeanReversion", pnl: "+$85.20" },
];

const gainers = [
    { symbol: "NVDA", price: "$122.50", change: "+4.2%" },
    { symbol: "AMD", price: "$165.20", change: "+3.8%" },
    { symbol: "MSFT", price: "$420.10", change: "+1.5%" },
];

const losers = [
    { symbol: "TSLA", price: "$172.40", change: "-2.1%" },
    { symbol: "AAPL", price: "$182.30", change: "-0.8%" },
];

export function Dashboard() {
    return (
        <div className="space-y-8 pb-10">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Executive Summary</h2>
                    <p className="text-muted-foreground">Portfolio metrics and proactive market intelligence.</p>
                </div>
                {/* AI Insights Highlight */}
                <div className="hidden lg:flex items-center gap-3 bg-primary/5 border border-primary/20 rounded-xl p-3 max-w-md">
                    <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></svg>
                    </div>
                    <div>
                        <div className="text-xs font-bold uppercase tracking-wider text-primary">AI Steward Active</div>
                        <div className="text-sm font-medium">Predicting high momentum in Semiconductors.</div>
                    </div>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-2xl border bg-card p-6 shadow-sm transition-all hover:shadow-md">
                    <div className="text-sm font-medium text-muted-foreground">Total Equity</div>
                    <div className="text-3xl font-bold mt-1">$112,450.00</div>
                    <div className="flex items-center gap-1 text-xs text-green-500 font-medium mt-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="m5 12 7-7 7 7" /><path d="M12 19V5" /></svg>
                        +12.4%
                    </div>
                </div>
                <div className="rounded-2xl border bg-card p-6 shadow-sm transition-all hover:shadow-md">
                    <div className="text-sm font-medium text-muted-foreground">Open Exposure</div>
                    <div className="text-3xl font-bold mt-1">$45,200.00</div>
                    <p className="text-xs text-muted-foreground mt-2">Risk Level: Moderate</p>
                </div>
                <div className="rounded-2xl border bg-card p-6 shadow-sm transition-all hover:shadow-md border-l-4 border-l-primary">
                    <div className="text-sm font-medium text-muted-foreground">AI Daily Alpha</div>
                    <div className="text-3xl font-bold mt-1 text-primary">+$1,450.00</div>
                    <p className="text-xs text-muted-foreground mt-2">Driven by Strategy: MeanReversion</p>
                </div>
                <div className="rounded-2xl border bg-card p-6 shadow-sm transition-all hover:shadow-md">
                    <div className="text-sm font-medium text-muted-foreground">System Health</div>
                    <div className="text-3xl font-bold mt-1">Optimal</div>
                    <div className="flex items-center gap-1 text-xs text-blue-500 font-medium mt-2">
                        9 Agents Operational
                    </div>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-12">
                {/* Main Graph */}
                <div className="md:col-span-8 rounded-2xl border bg-card/50 backdrop-blur-sm shadow-sm p-6 overflow-hidden">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h3 className="text-lg font-bold">Portfolio Performance</h3>
                            <p className="text-xs text-muted-foreground">Simulated growth over last 6 months</p>
                        </div>
                        <div className="flex bg-muted/30 p-1 rounded-lg gap-1">
                            {['1D', '1W', '1M', '6M', '1Y'].map(t => (
                                <button key={t} className={`px-3 py-1 text-[10px] font-bold rounded-md transition-colors ${t === '6M' ? 'bg-background shadow-sm text-primary' : 'text-muted-foreground hover:text-foreground'}`}>
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data}>
                                <defs>
                                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--ss-green)" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="var(--ss-green)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" opacity={0.05} vertical={false} />
                                <XAxis dataKey="name" stroke="#888888" fontSize={11} tickLine={false} axisLine={false} dy={10} />
                                <YAxis stroke="#888888" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v / 1000}k`} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderRadius: '12px', border: '1px solid hsl(var(--border))', fontSize: '12px' }}
                                />
                                <Line type="monotone" dataKey="value" stroke="var(--ss-green)" strokeWidth={3} dot={{ fill: 'var(--ss-green)', r: 4, strokeWidth: 0 }} activeDot={{ r: 6, strokeWidth: 0 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* AI Insights Sidebar */}
                <div className="md:col-span-4 flex flex-col gap-6">
                    <div className="rounded-2xl border bg-primary text-primary-foreground shadow-lg p-6 relative overflow-hidden">
                        <div className="relative z-10">
                            <h3 className="font-bold text-lg mb-2">Groq AI Prediction</h3>
                            <p className="text-xs text-primary-foreground/80 mb-6 leading-relaxed">
                                Our "Reasoning" model suggests high probability of upside in **Semiconductors (SOXX)** based on technical breakouts.
                            </p>
                            <div className="bg-white/10 rounded-xl p-4 backdrop-blur-md">
                                <div className="text-[10px] uppercase font-bold tracking-widest text-primary-foreground/60 mb-1">Steward Conviction</div>
                                <div className="text-2xl font-black">84% Strong Buy</div>
                            </div>
                        </div>
                        {/* Abstract Background Element */}
                        <div className="absolute -right-4 -bottom-4 h-32 w-32 bg-white/10 rounded-full blur-2xl" />
                    </div>

                    <div className="rounded-2xl border bg-card shadow-sm p-6">
                        <h3 className="font-bold text-sm mb-4 uppercase tracking-wider text-muted-foreground">Market Movers</h3>
                        <div className="space-y-4">
                            <div>
                                <div className="text-[10px] font-bold text-green-500 uppercase mb-2">Top Gainers</div>
                                {gainers.map(g => (
                                    <div key={g.symbol} className="flex items-center justify-between mb-2">
                                        <span className="text-sm font-bold">{g.symbol}</span>
                                        <span className="text-sm font-medium text-green-500">{g.change}</span>
                                    </div>
                                ))}
                            </div>
                            <div className="pt-2 border-t border-dashed">
                                <div className="text-[10px] font-bold text-red-500 uppercase mb-2">Top Losers</div>
                                {losers.map(l => (
                                    <div key={l.symbol} className="flex items-center justify-between mb-2">
                                        <span className="text-sm font-bold">{l.symbol}</span>
                                        <span className="text-sm font-medium text-red-500">{l.change}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Trading Agents Feed */}
            <div className="rounded-2xl border bg-card shadow-sm overflow-hidden">
                <div className="border-b p-6 flex items-center justify-between">
                    <h3 className="font-bold tracking-tight">Agent Audit Log</h3>
                    <div className="flex items-center gap-2">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                        </span>
                        <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Live Feed</span>
                    </div>
                </div>
                <div className="p-6">
                    <div className="space-y-6">
                        {activityItems.map((i) => (
                            <div key={i.id} className="flex items-start gap-4 pb-6 border-b border-dashed last:border-0 last:pb-0">
                                <div className="h-8 w-8 rounded-lg bg-muted flex items-center justify-center shrink-0">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20" /><path d="m17 5-5-3-5 3" /><path d="m17 19-5 3-5-3" /><path d="M2 12h20" /><path d="m5 7-3 5 3 5" /><path d="m19 7 3 5-3 5" /></svg>
                                </div>
                                <div className="flex-1 space-y-1">
                                    <div className="flex items-center justify-between">
                                        <p className="text-sm font-bold">{i.action}</p>
                                        <span className={`text-sm font-bold ${i.pnl.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>{i.pnl}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-xs text-muted-foreground">Agent: **StrategyAgent**</span>
                                        <span className="h-1 w-1 rounded-full bg-muted-foreground/30" />
                                        <span className="text-xs text-muted-foreground">Model: Groq Llama 3</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

