import React, { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import { Card } from "../components/ui/card";
import { ShieldCheck, Lock, ArrowRight, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { fetchUsers, loginUser } from '../services/api';

export function Login() {
    const { login } = useUser();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [users, setUsers] = useState([]);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    useEffect(() => {
        const loadUsers = async () => {
            const data = await fetchUsers();
            setUsers(Array.isArray(data) ? data : []);
            if (data && data.length > 0) {
                setEmail(data[0].email);
            }
        };
        loadUsers();
    }, []);

    const handleLogin = async () => {
        setLoading(true);
        try {
            const userData = await loginUser(email, password);
            if (!userData) {
                setLoading(false);
                return;
            }
            login({
                id: userData.id,
                name: userData.full_name || userData.email,
                email: userData.email,
                role: userData.role || 'TRADER',
                avatar: (userData.full_name || userData.email).slice(0, 2).toUpperCase()
            });
            navigate('/');
        } finally {
            setLoading(false);
        }
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
                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest">User</label>
                        <select
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold"
                        >
                            {users.map((u) => (
                                <option key={u.id} value={u.email}>{u.full_name || u.email} ({u.role || 'TRADER'})</option>
                            ))}
                        </select>
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

                    <button data-testid="login-submit" onClick={handleLogin} disabled={loading} className="w-full group relative p-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl transition-all flex items-center gap-3 text-left">
                        <div className="h-8 w-8 bg-white/10 rounded-lg flex items-center justify-center text-white"><Lock size={16} /></div>
                        <div className="flex-1"><h3 className="text-xs font-black text-white">Secure Login</h3><p className="text-[10px] text-white/60">Role-based access</p></div>
                        <ArrowRight size={14} className="text-white/70 group-hover:text-white transition-colors" />
                    </button>
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
