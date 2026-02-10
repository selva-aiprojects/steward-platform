import React, { useState } from "react"
import { Link, useLocation, NavLink } from "react-router-dom"
import {
    LayoutDashboard, Wallet, Users as UsersIcon, Menu, X,
    LogOut, Sun, Moon, Zap, BarChart2, ShieldCheck, FileText,
    Briefcase, Activity, HelpCircle, MessageSquare
} from "lucide-react"
import { useUser } from "../../context/UserContext"
import { useTheme } from "../theme-provider"
import logo from "../../assets/logo.png"
import { MarketTicker } from "../MarketTicker"
import ChatWidget from "../ChatWidget";

export function Layout({ children }) {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const location = useLocation();
    const { user, logout, isAdmin } = useUser();
    const { theme, toggleTheme } = useTheme();
    const buildSha = process.env.REACT_APP_BUILD_SHA || process.env.REACT_APP_GIT_SHA || "";
    const buildTime = process.env.REACT_APP_BUILD_TIME || "";
    const buildLabel = buildSha ? buildSha.slice(0, 7) : "dev";

    const closeMenu = () => setIsMobileMenuOpen(false);

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col md:flex-row">
            {/* Mobile Header */}
            <div className="md:hidden flex items-center justify-between p-4 bg-[#0A2A4D] text-white sticky top-0 z-50 shadow-md">
                <Link to="/" className="flex items-center gap-2">
                    <img src={logo} alt="Logo" className="h-6 w-6" />
                    <span className="font-heading font-black text-sm tracking-tight text-white">Stock<span className="text-green-400">Steward</span></span>
                </Link>
                <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 hover:bg-white/10 rounded-lg">
                    {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Sidebar */}
            <div className={`
                fixed inset-0 z-40 md:relative z-auto
                w-72 flex flex-col bg-[#0A2A4D] shadow-2xl transition-transform duration-300 ease-in-out
                ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
            `}>
                <div className="mb-10 p-8 hidden md:block">
                    <Link to="/" className="flex items-center gap-4 group">
                        <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 border border-white/20 shadow-xl overflow-hidden group-hover:scale-105 transition-transform">
                            <img src={logo} alt="Logo" className="h-10 w-10 object-contain" />
                        </div>
                        <div className="flex flex-col">
                            <div className="font-heading text-xl font-black tracking-tight text-white leading-none group-hover:text-green-400 transition-colors">
                                Stock<span className="text-primary text-green-400">Steward</span>
                            </div>
                            <span className="text-[10px] text-white/40 font-bold uppercase tracking-[0.2em] mt-1.5 ml-0.5">AI PLATFORM</span>
                        </div>
                    </Link>
                </div>

                <nav className="space-y-1.5 px-4 flex-1 py-6 md:py-0 overflow-y-auto">
                    <NavLink to="/" onClick={closeMenu} end className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                        <LayoutDashboard size={18} className={`${location.pathname === '/' ? 'text-primary' : 'text-slate-400 group-hover:text-primary'} transition-colors`} />
                        <span>Dashboard</span>
                    </NavLink>

                    {user?.role !== 'AUDITOR' && (
                        <>
                            <NavLink to="/trading" onClick={closeMenu} className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                                <Zap size={18} className={`${location.pathname === '/trading' ? 'text-green-400' : 'text-slate-400 group-hover:text-green-400'} transition-colors`} />
                                <span>Trading Hub</span>
                            </NavLink>
                            <NavLink to="/portfolio" onClick={closeMenu} className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                                <Briefcase size={18} className={`${location.pathname === '/portfolio' ? 'text-primary' : 'text-slate-400 group-hover:text-primary'} transition-colors`} />
                                <span>Portfolio</span>
                            </NavLink>
                            <NavLink to="/investment" onClick={closeMenu} className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                                <Activity size={18} className={`${location.pathname === '/investment' ? 'text-emerald-400' : 'text-slate-400 group-hover:text-emerald-400'} transition-colors`} />
                                <span>Investment</span>
                            </NavLink>
                        </>
                    )}

                    <NavLink to="/reports" end onClick={closeMenu} className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                        <BarChart2 size={18} className={`${location.pathname === '/reports' ? 'text-indigo-400' : 'text-slate-400 group-hover:text-indigo-400'} transition-colors`} />
                        <span>Reports</span>
                    </NavLink>
                    <NavLink to="/reports/investment" onClick={closeMenu} className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                        <BarChart2 size={18} className={`${location.pathname === '/reports/investment' ? 'text-emerald-400' : 'text-slate-400 group-hover:text-emerald-400'} transition-colors`} />
                        <span>Investment Reports</span>
                    </NavLink>

                    <NavLink to="/support" onClick={closeMenu} className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                        <MessageSquare size={18} className={`${location.pathname === '/support' ? 'text-pink-400' : 'text-slate-400 group-hover:text-pink-400'} transition-colors`} />
                        <span>Support</span>
                    </NavLink>

                    {(user?.role === 'TRADER' || user?.role === 'BUSINESS_OWNER') && (
                        <>
                            <div className="my-2 border-t border-white/10 mx-4" />
                            <Link to="/subscription" onClick={closeMenu} className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-black group hover:bg-amber-400/10 ${location.pathname === '/subscription' ? 'bg-amber-400/20 text-amber-400 border border-amber-400/20 shadow-lg shadow-amber-900/20' : 'text-amber-400/70 hover:text-amber-400'}`}>
                                <Zap size={18} className="fill-amber-400/20" />
                                <span className="tracking-wide">UPGRADE</span>
                            </Link>
                        </>
                    )}

                    {isAdmin && (
                        <>
                            <NavLink to="/users" onClick={closeMenu} className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                                <UsersIcon size={18} className={`${location.pathname === '/users' ? 'text-primary' : 'text-slate-400 group-hover:text-primary'} transition-colors`} />
                                <span>User Mgmt</span>
                            </NavLink>
                            <NavLink to="/kyc" onClick={closeMenu} className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all text-sm font-bold group ${isActive ? 'bg-white/10 text-white border border-white/5 shadow-xl' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}>
                                <FileText size={18} className={`${location.pathname === '/kyc' ? 'text-emerald-400' : 'text-slate-400 group-hover:text-emerald-400'} transition-colors`} />
                                <span>KYC Desk</span>
                            </NavLink>
                        </>
                    )}
                </nav>

                <div className="mt-auto p-4 border-t border-white/5 bg-black/20">
                    {user && (
                        <div className="flex items-center gap-3 mb-4 p-2 rounded-xl bg-white/5 border border-white/5">
                            <div className="h-8 w-8 rounded-lg bg-indigo-500/20 flex items-center justify-center text-[10px] font-black text-indigo-300 border border-indigo-500/20">
                                {user.avatar || user.name.slice(0, 2).toUpperCase()}
                            </div>
                            <div className="overflow-hidden">
                                <p className="text-xs font-black text-white leading-none truncate">{user.name}</p>
                                <p className="text-[9px] text-white/40 font-bold uppercase tracking-widest mt-1.5 truncate">{user.role}</p>
                            </div>
                        </div>
                    )}

                    <div className="flex gap-2">
                        <button
                            onClick={toggleTheme}
                            className="flex-1 flex items-center justify-center p-2.5 rounded-xl bg-white/5 border border-white/5 text-slate-400 hover:text-white hover:bg-white/10 transition-all"
                            aria-label="Toggle Theme"
                        >
                            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
                        </button>
                        <button
                            onClick={logout}
                            className="flex-[2] flex items-center justify-center gap-2 p-2.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-all font-black text-[10px] uppercase tracking-widest"
                        >
                            <LogOut size={14} />
                            <span>Logout</span>
                        </button>
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
            <main className="flex-1 w-full overflow-y-auto">
                <div className="sticky top-14 md:top-0 z-40 w-full animate-in fade-in duration-700">
                    <MarketTicker />
                </div>
                <div className="max-w-[1600px] mx-auto p-4 md:p-8">
                    {user && (
                        <div className="mb-8 p-6 rounded-2xl bg-white border border-slate-100 shadow-sm flex items-center justify-between animate-in fade-in slide-in-from-top-4 duration-500">
                            <div className="flex items-center gap-4">
                                <div className="h-12 w-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 shadow-inner">
                                    <ShieldCheck size={24} />
                                </div>
                                <div>
                                    <h2 className="text-sm font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Session Active</h2>
                                    <h1 className="text-xl font-black text-slate-900 leading-none">Greetings, <span className="text-primary">{user.name}</span>!!</h1>
                                </div>
                            </div>
                            <div className="hidden md:flex flex-col items-end gap-3">
                                <div className="flex items-center gap-3">
                                    <div className="flex flex-col items-end">
                                        <div className="flex items-center gap-2 mb-1">
                                            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest leading-none">Market Connection: Secure</span>
                                        </div>
                                        <span className="text-[10px] font-bold bg-[#0A2A4D] text-white px-3 py-1.5 rounded-lg border border-white/10 uppercase tracking-tighter">
                                            Role: {user.role}
                                        </span>
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <span className="text-[9px] font-black uppercase tracking-widest text-slate-400">Build</span>
                                        <span className="text-[10px] font-black bg-slate-100 text-slate-600 px-2 py-1 rounded-lg border border-slate-200 uppercase tracking-widest">
                                            {buildLabel}
                                        </span>
                                        {buildTime && (
                                            <span className="text-[8px] font-bold text-slate-400 mt-1">{buildTime}</span>
                                        )}
                                    </div>
                                    <Link
                                        to="/help"
                                        className="h-10 w-10 rounded-xl bg-slate-900 flex items-center justify-center text-white hover:bg-primary transition-all shadow-lg hover:shadow-primary/20 group"
                                        title="User Manual"
                                    >
                                        <HelpCircle size={20} className="group-hover:rotate-12 transition-transform" />
                                    </Link>
                                    <button
                                        onClick={logout}
                                        className="h-10 w-10 rounded-xl bg-red-50 flex items-center justify-center text-red-500 hover:bg-red-500 hover:text-white transition-all shadow-lg hover:shadow-red-500/20 group"
                                        title="Logout"
                                    >
                                        <LogOut size={20} className="group-hover:translate-x-0.5 transition-transform" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                    {children}
                </div>
            </main>
            <ChatWidget />
        </div>
    )
}