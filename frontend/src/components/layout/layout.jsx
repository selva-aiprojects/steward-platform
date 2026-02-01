import { ModeToggle } from "../components/mode-toggle"
import { Link } from "react-router-dom"
import { LayoutDashboard, Wallet, BookOpen, Users as UsersIcon } from "lucide-react"

export function Layout({ children }) {
    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Sidebar */}
            <div className="w-64 border-r bg-card p-4 flex flex-col">
                <div className="mb-8 pl-2">
                    <div className="flex items-center gap-2">
                        {/* Custom Shield Logo based on Brand Kit */}
                        <div className="relative flex h-8 w-8 items-center justify-center rounded bg-primary/20">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-6 w-6 text-primary">
                                <path fillRule="evenodd" d="M12.516 2.17a.75.75 0 00-1.032 0 11.209 11.209 0 01-7.877 3.08.75.75 0 00-.722.515A12.74 12.74 0 002.25 9.75c0 5.942 4.064 10.933 9.563 12.348a.749.749 0 00.374 0c5.499-1.415 9.563-6.406 9.563-12.348 0-1.352-.272-2.636-.759-3.807a.75.75 0 00-.722-.516l-.143.001c-2.996 0-5.717-1.17-7.734-3.08zm3.094 8.016a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="font-heading text-xl font-bold tracking-tight text-foreground">
                            Stock<span className="text-primary">Steward</span> <span className="text-muted-foreground font-normal">AI</span>
                        </div>
                    </div>
                    <div className="inline-flex items-center rounded-full border border-yellow-500/50 bg-yellow-500/10 px-2 py-0.5 text-[10px] font-semibold text-yellow-600 dark:text-yellow-400 mt-2 ml-1">
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
