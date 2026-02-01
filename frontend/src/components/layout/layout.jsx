import React, { useState } from "react"
import { Link, useLocation } from "react-router-dom"
import { LayoutDashboard, Wallet, Users as UsersIcon, Menu, X } from "lucide-react"
import logo from "../../assets/logo.png"

export function Layout({ children }) {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const location = useLocation();

    const closeMenu = () => setIsMobileMenuOpen(false);

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col md:flex-row">
            {/* Mobile Header */}
            <div className="md:hidden flex items-center justify-between p-4 bg-[#0A2A4D] text-white sticky top-0 z-50 shadow-md">
                <div className="flex items-center gap-2">
                    <img src={logo} alt="Logo" className="h-6 w-6" />
                    <span className="font-heading font-black text-sm tracking-tight text-white">Stock<span className="text-green-400">Steward</span></span>
                </div>
                <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 hover:bg-white/10 rounded-lg">
                    {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Sidebar */}
            <div className={`
                fixed inset-0 z-40 md:relative md:z-auto
                w-72 flex flex-col bg-[#0A2A4D] shadow-2xl transition-transform duration-300 ease-in-out
                ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
            `}>
                <div className="mb-10 p-8 hidden md:block">
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

                <nav className="space-y-2 px-6 flex-1 py-10 md:py-0 overflow-y-auto">
                    <Link to="/" onClick={closeMenu} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold group ${location.pathname === '/' ? 'bg-white/10 text-white' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
                        <LayoutDashboard size={20} className={`${location.pathname === '/' ? 'text-primary' : 'text-slate-400 group-hover:text-primary'} transition-colors`} />
                        <span>Dashboard</span>
                    </Link>
                    <Link to="/trading" onClick={closeMenu} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold group ${location.pathname === '/trading' ? 'bg-white/10 text-white' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
                        <div className={`flex h-6 w-6 items-center justify-center rounded-lg transition-all border ${location.pathname === '/trading' ? 'bg-green-500 text-white border-green-500' : 'bg-green-500/10 text-green-400 group-hover:bg-green-500 group-hover:text-white border-green-500/20'}`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20" /><path d="m17 5-5-3-5 3" /><path d="m17 19-5 3-5-3" /><path d="M2 12h20" /><path d="m5 7-3 5 3 5" /><path d="m19 7 3 5-3 5" /></svg>
                        </div>
                        <span>Trading Hub</span>
                    </Link>
                    <Link to="/portfolio" onClick={closeMenu} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold group ${location.pathname === '/portfolio' ? 'bg-white/10 text-white' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
                        <Wallet size={20} className={`${location.pathname === '/portfolio' ? 'text-primary' : 'text-slate-400 group-hover:text-primary'} transition-colors`} />
                        <span>Portfolio</span>
                    </Link>
                    <Link to="/reports" onClick={closeMenu} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold group ${location.pathname === '/reports' ? 'bg-white/10 text-white' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`${location.pathname === '/reports' ? 'text-primary' : 'text-slate-400 group-hover:text-primary'} transition-colors`}><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" /><path d="M14 2v4a2 2 0 0 0 2 2h4" /><path d="M10 9H8" /><path d="M16 13H8" /><path d="M16 17H8" /></svg>
                        <span>Reports</span>
                    </Link>
                    <Link to="/users" onClick={closeMenu} className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-bold group ${location.pathname === '/users' ? 'bg-white/10 text-white' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}>
                        <UsersIcon size={20} className={`${location.pathname === '/users' ? 'text-primary' : 'text-slate-400 group-hover:text-primary'} transition-colors`} />
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

            {/* Mobile Overlay */}
            {isMobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-30 md:hidden"
                    onClick={closeMenu}
                />
            )}

            {/* Main Content */}
            <main className="flex-1 p-4 md:p-8 overflow-y-auto w-full">
                <div className="max-w-[1600px] mx-auto">
                    {children}
                </div>
            </main>
        </div>
    )
}
