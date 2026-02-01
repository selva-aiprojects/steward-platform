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
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-center">
                                <div className="ml-4 space-y-1">
                                    <p className="text-sm font-medium leading-none">Bought AAPL</p>
                                    <p className="text-xs text-muted-foreground">Strategy: SMACrossover</p>
                                </div>
                                <div className="ml-auto font-medium">+$250.00</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
