import { ModeToggle } from "../mode-toggle"
import { Link } from "react-router-dom"
import { LayoutDashboard, Wallet, BookOpen, Users as UsersIcon } from "lucide-react"
import logo from "../../assets/logo.png"

export function Layout({ children }) {
    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Sidebar */}
            <div className="w-68 border-r border-slate-100 flex flex-col relative" style={{ background: 'var(--bg-sidebar)' }}>
                <div className="mb-8 p-6">
                    <div className="flex items-center gap-3">
                        <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 backdrop-blur-md border border-white/10 shadow-lg">
                            <img src={logo} alt="Logo" className="h-7 w-7" />
                        </div>
                        <div className="font-heading text-xl font-black tracking-tight text-white">
                            Stock<span className="text-primary">Steward</span> <span className="text-white/40 font-normal">AI</span>
                        </div>
                    </div>
                </div>

                <nav className="space-y-1.5 px-4 flex-1">
                    <Link to="/" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-sm font-bold text-white/60 hover:text-white group">
                        <LayoutDashboard size={18} className="group-hover:text-primary transition-colors" />
                        Executive Dashboard
                    </Link>
                    <Link to="/trading" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-sm font-bold text-white/60 hover:text-white group">
                        <div className="flex h-5 w-5 items-center justify-center rounded bg-primary/20 text-primary group-hover:bg-primary group-hover:text-white transition-all">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20" /><path d="m17 5-5-3-5 3" /><path d="m17 19-5 3-5-3" /><path d="M2 12h20" /><path d="m5 7-3 5 3 5" /><path d="m19 7 3 5-3 5" /></svg>
                        </div>
                        Trading Hub
                    </Link>
                    <Link to="/portfolio" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-sm font-bold text-white/60 hover:text-white group">
                        <Wallet size={18} className="group-hover:text-primary transition-colors" />
                        My Portfolio
                    </Link>
                    <Link to="/reports" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-sm font-bold text-white/60 hover:text-white group">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:text-primary transition-colors"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" /><path d="M14 2v4a2 2 0 0 0 2 2h4" /><path d="M10 9H8" /><path d="M16 13H8" /><path d="M16 17H8" /></svg>
                        Strategy Reports
                    </Link>
                    <Link to="/users" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-sm font-bold text-white/60 hover:text-white group">
                        <UsersIcon size={18} className="group-hover:text-primary transition-colors" />
                        User Management
                    </Link>
                </nav>

                <div className="mt-auto p-6 border-t border-white/5 bg-black/20">
                    <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-[10px] font-black text-primary border border-primary/20">
                            SS
                        </div>
                        <div>
                            <p className="text-xs font-black text-white leading-none">Admin Terminal</p>
                            <p className="text-[10px] text-white/40 font-bold uppercase tracking-widest mt-1">Live Connection</p>
                        </div>
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
