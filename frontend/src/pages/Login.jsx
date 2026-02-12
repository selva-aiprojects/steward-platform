import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { Card } from "../components/ui/card";
import { ShieldCheck, Lock, ArrowRight, Loader2 } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../services/api';

export function Login() {
    const { login, user } = useUser();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [rememberMe, setRememberMe] = useState(true);

    useEffect(() => {
        if (user) {
            navigate('/');
            return;
        }
    }, [user, navigate]);

    const performLogin = async (emailValue, passwordValue, rememberOverride = rememberMe) => {
        setError('');
        const trimmedEmail = (emailValue || '').trim();
        const trimmedPassword = (passwordValue || '').trim();
        if (!trimmedEmail || !trimmedPassword) {
            setError('Enter email and password.');
            return;
        }
        setLoading(true);
        try {
            const userData = await loginUser(trimmedEmail, trimmedPassword);
            if (!userData) {
                setError('Invalid credentials or server unavailable.');
                setLoading(false);
                return;
            }
            const session = {
                id: userData.id,
                name: userData.full_name || userData.email,
                email: userData.email,
                role: userData.role || 'TRADER',
                avatar: (userData.full_name || userData.email).slice(0, 2).toUpperCase()
            };
            login(session);
            if (!rememberOverride) {
                localStorage.removeItem('stocksteward_user');
            }
            navigate('/');
        } catch (err) {
            setError('Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleLogin = async () => {
        await performLogin(email, password);
    };

    const quickLogin = async (role) => {
        const credentials = {
            admin: { email: 'admin@stocksteward.ai', password: 'admin123' },
            trader: { email: 'alex@stocksteward.ai', password: 'trader123' },
            auditor: { email: 'auditor@stocksteward.ai', password: 'audit123' },
            'business-owner': { email: 'owner@stocksteward.ai', password: 'owner123' }
        };
        const creds = credentials[role];
        if (!creds) {
            return;
        }
        setEmail(creds.email);
        setPassword(creds.password);
        await performLogin(creds.email, creds.password);
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50 relative overflow-hidden">
            {/* Background elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-[-12%] left-[-12%] w-[55%] h-[55%] bg-emerald-300/30 rounded-full blur-[140px]" />
                <div className="absolute bottom-[-12%] right-[-12%] w-[55%] h-[55%] bg-emerald-500/20 rounded-full blur-[160px]" />
                <div className="absolute inset-0 opacity-30" style={{ backgroundImage: "radial-gradient(circle at 1px 1px, rgba(16,185,129,0.2) 1px, transparent 0)", backgroundSize: "24px 24px" }} />
            </div>

            <Card className="w-full max-w-md bg-white border-slate-200 shadow-2xl z-10 p-8 rounded-2xl">
                <div className="flex flex-col items-center mb-8">
                    <div className="h-16 w-16 bg-emerald-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-emerald-500/30">
                        <ShieldCheck className="text-white" size={32} />
                    </div>
                    <h1 className="text-2xl font-black text-slate-900 tracking-tight">StockSteward AI</h1>
                    <p className="text-sm text-slate-500 font-medium mt-1">Institutional Grade Wealth Management</p>
                </div>

                <div className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">User</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="user@stocksteward.ai"
                            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Use: trader123 / admin123 / owner123 / audit123"
                            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold"
                        />
                    </div>

                    <label className="flex items-center gap-2 text-[10px] font-black text-slate-500 uppercase tracking-widest">
                        <input
                            type="checkbox"
                            checked={rememberMe}
                            onChange={(e) => setRememberMe(e.target.checked)}
                            className="h-4 w-4 rounded border-slate-300"
                        />
                        Remember Me
                    </label>

                    <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-50 border border-slate-100 rounded-lg px-3 py-2">
                        Demo Logins: admin@stocksteward.ai / admin123 · owner@stocksteward.ai / owner123 · alex@stocksteward.ai / trader123 · sarah.c@sky.net / trader123 · tony@starkintl.ai / trader123 · bruce@waynecorp.com / trader123 · nat@shield.gov / trader123 · auditor@stocksteward.ai / audit123
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-[10px] font-black uppercase tracking-widest">
                        <button type="button" data-testid="login-admin" onClick={() => quickLogin('admin')} className="rounded-lg border border-slate-200 bg-white px-2 py-2 text-slate-600 hover:bg-slate-50">
                            Admin
                        </button>
                        <button type="button" data-testid="login-business-owner" onClick={() => quickLogin('business-owner')} className="rounded-lg border border-slate-200 bg-white px-2 py-2 text-slate-600 hover:bg-slate-50">
                            Business Owner
                        </button>
                        <button type="button" data-testid="login-trader" onClick={() => quickLogin('trader')} className="rounded-lg border border-slate-200 bg-white px-2 py-2 text-slate-600 hover:bg-slate-50">
                            Trader
                        </button>
                        <button type="button" data-testid="login-auditor" onClick={() => quickLogin('auditor')} className="rounded-lg border border-slate-200 bg-white px-2 py-2 text-slate-600 hover:bg-slate-50">
                            Auditor
                        </button>
                    </div>

                    {error && (
                        <div className="text-[10px] font-black text-red-500 uppercase tracking-widest bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                            {error}
                        </div>
                    )}

                    <button data-testid="login-submit" onClick={handleLogin} disabled={loading} className="w-full group relative p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition-all flex items-center gap-3 text-left shadow-lg shadow-emerald-600/20">
                        <div className="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center text-white"><Lock size={16} /></div>
                        <div className="flex-1"><h3 className="text-xs font-black text-white">Secure Login</h3><p className="text-[10px] text-white/60">Role-based access</p></div>
                        <ArrowRight size={14} className="text-white/70 group-hover:text-white transition-colors" />
                    </button>
                    <Link
                        to="/kyc"
                        className="w-full group relative p-3 bg-white border border-emerald-200 text-emerald-700 rounded-xl transition-all flex items-center gap-3 text-left shadow-sm hover:shadow-md"
                    >
                        <div className="h-8 w-8 bg-emerald-50 rounded-lg flex items-center justify-center text-emerald-600"><ShieldCheck size={16} /></div>
                        <div className="flex-1"><h3 className="text-xs font-black">Start KYC Application</h3><p className="text-[10px] text-emerald-600/70">New investor onboarding</p></div>
                        <ArrowRight size={14} className="text-emerald-500/70 group-hover:text-emerald-700 transition-colors" />
                    </Link>
                </div>

                {loading && (
                    <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center rounded-2xl z-20">
                        <Loader2 className="animate-spin text-primary" size={32} />
                    </div>
                )}

                <div className="mt-8 text-center">
                    <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Secure Access - 256-bit Encryption</p>
                </div>
            </Card>
        </div>
    );
}
