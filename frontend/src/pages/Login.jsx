import React, { useState } from 'react';
import { useUser } from '../context/UserContext';
import { Card } from "../components/ui/card";
import { ShieldCheck, User, Lock, ArrowRight, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Login() {
    const { login } = useUser();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleLogin = (role) => {
        setLoading(true);
        // Simulate API delay
        setTimeout(() => {
            if (role === 'ADMIN') {
                login({
                    id: 999,
                    name: 'Super Admin',
                    email: 'admin@stocksteward.ai',
                    role: 'ADMIN',
                    avatar: 'SA'
                });
            } else {
                login({
                    id: 1,
                    name: 'Demo User',
                    email: 'user@example.com',
                    role: 'USER',
                    avatar: 'DU'
                });
            }
            setLoading(false);
            navigate('/');
        }, 800);
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-slate-900 relative overflow-hidden">
            {/* Background elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-600/20 rounded-full blur-[120px]" />
            </div>

            <Card className="w-full max-w-md bg-white/95 backdrop-blur-xl border-slate-200 shadow-2xl z-10 p-8 rounded-2xl">
                <div className="flex flex-col items-center mb-8">
                    <div className="h-16 w-16 bg-[#0A2A4D] rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-indigo-900/20">
                        <ShieldCheck className="text-white" size={32} />
                    </div>
                    <h1 className="text-2xl font-black text-slate-900 tracking-tight">StockSteward AI</h1>
                    <p className="text-sm text-slate-500 font-medium mt-1">Institutional Grade Wealth Management</p>
                </div>

                <div className="space-y-4">
                    <button
                        onClick={() => handleLogin('ADMIN')}
                        disabled={loading}
                        className="w-full group relative p-4 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl transition-all flex items-center gap-4 text-left"
                    >
                        <div className="h-10 w-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-700">
                            <Lock size={20} />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-sm font-black text-slate-900">Super Admin Portal</h3>
                            <p className="text-xs text-slate-500">Configure users & system parameters</p>
                        </div>
                        <ArrowRight size={16} className="text-slate-300 group-hover:text-indigo-600 transition-colors" />
                    </button>

                    <button
                        onClick={() => handleLogin('USER')}
                        disabled={loading}
                        className="w-full group relative p-4 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl transition-all flex items-center gap-4 text-left"
                    >
                        <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center text-green-700">
                            <User size={20} />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-sm font-black text-slate-900">Portfolio Manager</h3>
                            <p className="text-xs text-slate-500">Access your investments & trading hub</p>
                        </div>
                        <ArrowRight size={16} className="text-slate-300 group-hover:text-green-600 transition-colors" />
                    </button>
                </div>

                {loading && (
                    <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center rounded-2xl z-20">
                        <Loader2 className="animate-spin text-primary" size={32} />
                    </div>
                )}

                <div className="mt-8 text-center">
                    <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Secure Access • 256-bit Encryption</p>
                </div>
            </Card>
        </div>
    );
}
