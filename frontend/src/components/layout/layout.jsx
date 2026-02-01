import { ModeToggle } from "../components/mode-toggle"
import { Link } from "react-router-dom"
import { LayoutDashboard, Wallet, BookOpen } from "lucide-react"

export function Layout({ children }) {
    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Sidebar */}
            <div className="w-64 border-r bg-card p-4 flex flex-col">
                <div className="mb-8">
                    <div className="font-bold text-2xl text-primary">StockSteward</div>
                    <div className="inline-flex items-center rounded-full border border-yellow-500/50 bg-yellow-500/10 px-2 py-0.5 text-xs font-semibold text-yellow-600 dark:text-yellow-400 mt-1">
                        PAPER TRADING
                    </div>
                </div>

                <nav className="space-y-2 flex-1">
                    <Link to="/" className="flex items-center gap-2 p-2 rounded hover:bg-accent text-sm font-medium">
                        <LayoutDashboard size={18} />
                        Dashboard
                    </Link>
                    <Link to="/portfolio" className="flex items-center gap-2 p-2 rounded hover:bg-accent text-sm font-medium">
                        <Wallet size={18} />
                        Portfolio
                    </Link>
                    <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="flex items-center gap-2 p-2 rounded hover:bg-accent text-sm font-medium">
                        <BookOpen size={18} />
                        API Docs
                    </a>
                </nav>

                <div className="mt-auto pt-4 border-t">
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">v0.1.0</span>
                        <ModeToggle />
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <main className="flex-1 p-8 overflow-y-auto">
                {children}
            </main>
        </div>
    )
}
