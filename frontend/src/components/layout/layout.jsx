import { ModeToggle } from "../mode-toggle"
import { Link } from "react-router-dom"
import { LayoutDashboard, Wallet, BookOpen, Users as UsersIcon } from "lucide-react"
import logo from "../../assets/logo.png"

export function Layout({ children }) {
    return (
        <div className="min-h-screen bg-background text-foreground flex">
            {/* Sidebar */}
            <div className="w-72 flex flex-col relative bg-[#0A2A4D] shadow-2xl">
                <div className="mb-10 p-8">
                    <div className="flex items-center gap-4">
                        <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 border border-white/20 shadow-xl overflow-hidden">
                            <img src={logo} alt="Logo" className="h-10 w-10 object-contain" />
                        </div>
                        <div className="flex flex-col">
                            <div className="font-heading text-xl font-black tracking-tight text-white leading-none">
                                Stock<span className="text-primary text-green-400">Steward</span>
                            </div>
                            <span className="text-[10px] text-white/40 font-bold uppercase tracking-[0.2em] mt-1.5 ml-0.5">AI PLATFORM</span>
                        </div>
                    </div>
                </div>

                <nav className="space-y-2 px-6 flex-1">
                    <Link to="/" className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold text-slate-300 hover:text-white hover:bg-white/5 group">
                        <LayoutDashboard size={20} className="group-hover:text-primary text-slate-400 transition-colors" />
                        <span>Dashboard</span>
                    </Link>
                    <Link to="/trading" className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold text-slate-300 hover:text-white hover:bg-white/5 group">
                        <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-green-500/10 text-green-400 group-hover:bg-green-500 group-hover:text-white transition-all border border-green-500/20">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20" /><path d="m17 5-5-3-5 3" /><path d="m17 19-5 3-5-3" /><path d="M2 12h20" /><path d="m5 7-3 5 3 5" /><path d="m19 7 3 5-3 5" /></svg>
                        </div>
                        <span>Trading Hub</span>
                    </Link>
                    <Link to="/portfolio" className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold text-slate-300 hover:text-white hover:bg-white/5 group">
                        <Wallet size={20} className="group-hover:text-primary text-slate-400 transition-colors" />
                        <span>Portfolio</span>
                    </Link>
                    <Link to="/reports" className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold text-slate-300 hover:text-white hover:bg-white/5 group">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:text-primary text-slate-400 transition-colors"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" /><path d="M14 2v4a2 2 0 0 0 2 2h4" /><path d="M10 9H8" /><path d="M16 13H8" /><path d="M16 17H8" /></svg>
                        <span>Reports</span>
                    </Link>
                    <Link to="/users" className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold text-slate-300 hover:text-white hover:bg-white/5 group">
                        <UsersIcon size={20} className="group-hover:text-primary text-slate-400 transition-colors" />
                        <span>Users</span>
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
