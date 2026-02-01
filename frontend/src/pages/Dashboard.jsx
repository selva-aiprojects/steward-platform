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

export function Dashboard() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                <p className="text-muted-foreground">Overview of your simulated performance.</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
                    <div className="text-sm font-medium">Total Equity</div>
                    <div className="text-2xl font-bold">$112,000.00</div>
                    <p className="text-xs text-muted-foreground">+12% from start</p>
                </div>
                <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
                    <div className="text-sm font-medium">Unrealized PnL</div>
                    <div className="text-2xl font-bold text-green-500">+$4,500.00</div>
                </div>
                <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
                    <div className="text-sm font-medium">Realized PnL</div>
                    <div className="text-2xl font-bold text-green-500">+$7,500.00</div>
                </div>
                <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
                    <div className="text-sm font-medium">Win Rate</div>
                    <div className="text-2xl font-bold">68%</div>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-7">
                <div className="col-span-4 rounded-xl border bg-card text-card-foreground shadow p-6">
                    <div className="mb-4">
                        <h3 className="font-semibold">Equity Curve</h3>
                    </div>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" opacity={0.1} vertical={false} />
                                <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value / 1000}k`} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', color: 'hsl(var(--foreground))' }}
                                    itemStyle={{ color: 'hsl(var(--foreground))' }}
                                />
                                <Line type="monotone" dataKey="value" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="col-span-3 rounded-xl border bg-card text-card-foreground shadow p-6">
                    <h3 className="font-semibold mb-4">Recent Activity</h3>
                    <div className="space-y-4">
                        {/* Mock Items */}
                        {activityItems.length > 0 ? (
                            activityItems.map((i) => (
                                <div key={i} className="flex items-center">
                                    <div className="ml-4 space-y-1">
                                        <p className="text-sm font-medium leading-none">Bought AAPL</p>
                                        <p className="text-xs text-muted-foreground">Strategy: SMACrossover</p>
                                    </div>
                                    <div className="ml-auto font-medium">+$250.00</div>
                                </div>
                            ))
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-muted-foreground bg-muted/5 rounded-lg border border-dashed p-8 text-center transition-all hover:bg-muted/10">
                                <div className="rounded-full bg-background p-4 mb-4 shadow-sm ring-1 ring-border">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-bar-chart-2 opacity-50"><line x1="18" x2="18" y1="20" y2="10" /><line x1="12" x2="12" y1="20" y2="4" /><line x1="6" x2="6" y1="20" y2="14" /></svg>
                                </div>
                                <h3 className="font-semibold text-lg text-foreground mb-1">Waiting for Market Data</h3>
                                <p className="text-sm max-w-sm mx-auto mb-4">
                                    Your agents are ready. Once the simulation creates orders, your equity curve will populate here in real-time.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
