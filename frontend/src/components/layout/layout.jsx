import { ModeToggle } from "../mode-toggle"
import { Link } from "react-router-dom"
import { LayoutDashboard, Wallet, BookOpen, Users as UsersIcon } from "lucide-react"
import logo from "../../assets/logo.png"

export function Layout({ children }) {
    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Sidebar */}
            <div className="w-64 border-r bg-card p-4 flex flex-col">
                <div className="mb-0 pl-1 py-1">
                    <Link to="/" className="flex items-center gap-3 group">
                        <div className="relative flex h-10 w-10 items-center justify-center rounded-lg bg-primary/5 p-1 transition-all group-hover:scale-110">
                            <img src={logo} alt="StockSteward Logo" className="h-full w-full object-contain" />
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

                <nav className="space-y-1 flex-1">
                    <Link to="/" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-sm font-medium text-white/70 hover:text-white">
                        <LayoutDashboard size={18} />
                        Executive Dashboard
                    </Link>
                    <Link to="/trading" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-sm font-medium text-white/70 hover:text-white">
                        <div className="flex h-5 w-5 items-center justify-center rounded bg-primary/20 text-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20" /><path d="m17 5-5-3-5 3" /><path d="m17 19-5 3-5-3" /><path d="M2 12h20" /><path d="m5 7-3 5 3 5" /><path d="m19 7 3 5-3 5" /></svg>
                        </div>
                        Trading Hub
                    </Link>
                    <Link to="/portfolio" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-sm font-medium text-white/70 hover:text-white">
                        <Wallet size={18} />
                        My Portfolio
                    </Link>
                    <Link to="/reports" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-sm font-medium text-white/70 hover:text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-file-text"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" /><path d="M14 2v4a2 2 0 0 0 2 2h4" /><path d="M10 9H8" /><path d="M16 13H8" /><path d="M16 17H8" /></svg>
                        Strategy Reports
                    </Link>
                    <Link to="/users" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-sm font-medium text-white/70 hover:text-white">
                        <UsersIcon size={18} />
                        User Management
                    </Link>
                    <div className="pt-4 mt-4 border-t border-white/10">
                        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-sm font-medium text-white/40 hover:text-white">
                            <BookOpen size={18} />
                            API Specs
                        </a>
                    </div>
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
