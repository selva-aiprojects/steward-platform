export function Portfolio() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Portfolio</h2>
                <p className="text-muted-foreground">Current holdings and open positions.</p>
            </div>

            <div className="rounded-md border bg-card">
                <div className="relative w-full overflow-auto">
                    <table className="w-full caption-bottom text-sm">
                        <thead className="[&_tr]:border-b">
                            <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Symbol</th>
                                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Quantity</th>
                                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Avg Price</th>
                                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Current Price</th>
                                <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Value</th>
                                <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Unrealized PnL</th>
                            </tr>
                        </thead>
                        <tbody className="[&_tr:last-child]:border-0">
                            <tr className="border-b transition-colors hover:bg-muted/50">
                                <td className="p-4 align-middle font-medium">AAPL</td>
                                <td className="p-4 align-middle">50</td>
                                <td className="p-4 align-middle">$145.00</td>
                                <td className="p-4 align-middle">$150.00</td>
                                <td className="p-4 align-middle text-right">$7,500.00</td>
                                <td className="p-4 align-middle text-right text-green-500">+$250.00</td>
                            </tr>
                            <tr className="border-b transition-colors hover:bg-muted/50">
                                <td className="p-4 align-middle font-medium">MSFT</td>
                                <td className="p-4 align-middle">20</td>
                                <td className="p-4 align-middle">$310.00</td>
                                <td className="p-4 align-middle">$320.00</td>
                                <td className="p-4 align-middle text-right">$6,400.00</td>
                                <td className="p-4 align-middle text-right text-green-500">+$200.00</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
