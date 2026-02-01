import { ModeToggle } from "../mode-toggle"
import { Link } from "react-router-dom"
import { LayoutDashboard, Wallet, BookOpen, Users as UsersIcon } from "lucide-react"

export function Layout({ children }) {
    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Sidebar */}
            <div className="w-64 border-r bg-card p-4 flex flex-col">
                <div className="mb-0 pl-1 py-1">
                    <Link to="/" className="flex items-center gap-3 group">
                        <div className="relative flex h-10 w-10 items-center justify-center rounded-lg bg-primary/5 p-1 transition-all group-hover:scale-110">
                            <img src="/logo.png" alt="StockSteward Logo" className="h-full w-full object-contain" />
                        </div>
                        <div className="flex flex-col">
                            <div className="font-heading text-xl font-bold tracking-tight text-foreground leading-none">
                                Stock<span className="text-primary">Steward</span>
                            </div>
                            <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-[0.2em] mt-1 ml-0.5">AI Platform</span>
                        </div>
                    </Link>
                    <div className="inline-flex items-center rounded-full border border-yellow-500/50 bg-yellow-500/10 px-2 py-0.5 text-[10px] font-semibold text-yellow-600 dark:text-yellow-400 mt-3 ml-0.5">
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
                    <Link to="/users" className="flex items-center gap-2 p-2 rounded hover:bg-accent text-sm font-medium">
                        <UsersIcon size={18} />
                        Users
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
