import React, { useEffect, useState } from 'react';
import { Card } from "../components/ui/card";
import { User, Wallet, Shield, PieChart, ArrowUpRight, ArrowDownRight, Loader2 } from "lucide-react";
import { fetchUsers, fetchAllPortfolios, updateUser, createAuditLog } from "../services/api";
import { useUser } from "../context/UserContext";

export function Users() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                const [usersData, portfoliosData] = await Promise.all([
                    fetchUsers(),
                    fetchAllPortfolios()
                ]);

                // Map users to their portfolios
                const combined = usersData.map(user => {
                    const portfolio = portfoliosData.find(p => p.user_id === user.id) || {
                        invested_amount: 0,
                        cash_balance: 0,
                        win_rate: 0
                    };
                    return {
                        id: user.id,
                        name: user.full_name,
                        email: user.email,
                        status: user.is_active ? "ACTIVE" : "INACTIVE",
                        used: portfolio.invested_amount,
                        unused: portfolio.cash_balance,
                        risk: user.risk_tolerance,
                        win_rate: `${portfolio.win_rate}%`
                    };
                });
                setUsers(combined);
            } catch (err) {
                console.error("Failed to load user data from backend:", err);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) {
        return (
            <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400">
                <Loader2 className="animate-spin mb-4" size={32} />
                <p className="font-bold uppercase text-[10px] tracking-widest">Bridging Secure DB Connection...</p>
            </div>
        );
    }

    const [selectedUser, setSelectedUser] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Form States
    const [tradingMode, setTradingMode] = useState('AUTO');
    const [allowedSectors, setAllowedSectors] = useState(['Technology']);
    const [adminComment, setAdminComment] = useState('');

    const openManageModal = (user) => {
        setSelectedUser(user);
        setTradingMode(user.trading_mode || 'AUTO');
        // Parse sectors if string or array
        const sectors = user.allowed_sectors ?
            (Array.isArray(user.allowed_sectors) ? user.allowed_sectors : user.allowed_sectors.split(','))
            : ['Technology'];
        setAllowedSectors(sectors);
        setIsModalOpen(true);
    };

    const toggleSector = (sector) => {
        if (allowedSectors.includes(sector)) {
            setAllowedSectors(allowedSectors.filter(s => s !== sector));
        } else {
            setAllowedSectors([...allowedSectors, sector]);
        }
    };

    const { user: currentUser } = useUser();

    const handleSaveConfig = async () => {
        try {
            // 1. Update User Policy
            await updateUser(selectedUser.id, {
                trading_mode: tradingMode,
                allowed_sectors: allowedSectors.join(','),
                // We don't send admin comment to update user, only to audit
            });

            // 2. Create Audit Log
            if (currentUser) {
                await createAuditLog({
                    action: "UPDATE_USER_POLICY",
                    admin_id: currentUser.id,
                    target_user_id: selectedUser.id,
                    details: JSON.stringify({ tradingMode, allowedSectors }),
                    reason: adminComment
                });
            }

            // Optimistic Update
            setUsers(users.map(u => u.id === selectedUser.id ? {
                ...u,
                trading_mode: tradingMode,
                allowed_sectors: allowedSectors
            } : u));

            setIsModalOpen(false);
            setAdminComment('');
            alert("Policy updated successfully and logged in audit trail.");
        } catch (error) {
            console.error("Failed to save configuration:", error);
            alert("Failed to update user policy. Please checks logs.");
        }
    };

    const SECTORS = ['Technology', 'Healthcare', 'Manufacturing', 'Finance', 'Energy', 'Consumer'];

    return (
        <div data-testid="users-container" className="space-y-8 animate-in fade-in duration-500 relative">
            <header>
                <h1 className="text-3xl font-black text-slate-900 font-heading">User Equity Management</h1>
                <p className="text-slate-500 uppercase text-[10px] font-bold tracking-[0.2em] mt-1">Allocation Audit & Risk Tracking</p>
            </header>

            <div className="grid grid-cols-1 gap-6">
                {users.map((user) => (
                    <Card key={user.id} className="p-0 border-slate-100 shadow-sm overflow-hidden bg-white hover:border-primary/20 transition-all group">
                        <div className="flex flex-col lg:flex-row">
                            {/* Profile Info */}
                            <div className="p-6 lg:w-1/4 border-b lg:border-b-0 lg:border-r border-slate-50 bg-slate-50/30">
                                <div className="flex items-center gap-4">
                                    <div className="h-12 w-12 rounded-full bg-slate-900 flex items-center justify-center text-white font-black text-xs">
                                        {user.name.split(' ').map(n => n[0]).join('')}
                                    </div>
                                    <div>
                                        <h3 className="font-black text-slate-900 leading-none">{user.name}</h3>
                                        <p className="text-[10px] text-slate-400 font-bold mt-1 uppercase tracking-tighter">{user.email}</p>
                                    </div>
                                </div>
                                <div className="mt-4 flex items-center gap-2 flex-wrap">
                                    <span className={`px-2 py-0.5 rounded text-[8px] font-black tracking-widest uppercase ${user.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-400'
                                        }`}>{user.status}</span>
                                    <span className="text-[10px] text-slate-500 font-bold">Risk: {user.risk}</span>
                                    <span className={`px-2 py-0.5 rounded text-[8px] font-black tracking-widest uppercase border ${user.trading_mode === 'MANUAL' ? 'bg-orange-50 text-orange-600 border-orange-100' : 'bg-blue-50 text-blue-600 border-blue-100'}`}>
                                        {user.trading_mode || 'AUTO'}
                                    </span>
                                </div>
                                <button
                                    data-testid="manage-config-button"
                                    onClick={() => openManageModal(user)}
                                    className="mt-4 w-full py-2 bg-white border border-slate-200 text-slate-600 text-[10px] font-black uppercase tracking-widest rounded-lg hover:bg-slate-50 hover:text-primary transition-colors hover:border-primary/30"
                                >
                                    Manage Configuration
                                </button>
                            </div>

                            {/* Fund Report & Stats */}
                            <div className="p-6 flex-1 flex flex-col md:flex-row items-center justify-between gap-8">
                                <div className="flex-1 w-full space-y-4">
                                    <div className="flex justify-between items-end">
                                        <div>
                                            <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest">Fund Utilization</p>
                                            <p className="text-lg font-black text-slate-900 mt-1">${(user.used + user.unused).toLocaleString()}</p>
                                        </div>
                                        <div className="text-right">
                                            <span className="text-[10px] font-black text-primary uppercase">Total Equity</span>
                                        </div>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden flex shadow-inner">
                                        <div
                                            className="h-full bg-primary shadow-[0_0_10px_rgba(45,189,66,0.5)]"
                                            style={{ width: `${(user.used / (user.used + user.unused)) * 100}%` }}
                                        />
                                    </div>

                                    <div className="flex justify-between text-[10px] font-black uppercase tracking-tight">
                                        <div className="flex items-center gap-1.5 text-primary">
                                            <div className="h-2 w-2 rounded-full bg-primary" />
                                            Used: ${user.used.toLocaleString()}
                                        </div>
                                        <div className="flex items-center gap-1.5 text-slate-400">
                                            <div className="h-2 w-2 rounded-full bg-slate-200" />
                                            Idle: ${user.unused.toLocaleString()}
                                        </div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 lg:w-1/3">
                                    <div className="p-4 rounded-2xl bg-slate-50/50 border border-slate-100">
                                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-tighter leading-none mb-1">Win Rate</p>
                                        <p className="text-xl font-black text-slate-900">{user.win_rate}</p>
                                    </div>
                                    <div className="p-4 rounded-2xl bg-slate-50/50 border border-slate-100">
                                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-tighter leading-none mb-1">Utilization</p>
                                        <p className="text-xl font-black text-primary">
                                            {((user.used / (user.used + user.unused)) * 100).toFixed(0)}%
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </Card>
                ))}
            </div>

            {/* Admin Configuration Modal */}
            {isModalOpen && selectedUser && (
                <div data-testid="policy-modal" className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
                    <Card className="w-full max-w-lg bg-white border-0 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 p-0">
                        <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                            <div>
                                <h3 className="text-lg font-black text-slate-900 font-heading">Configure User Policy</h3>
                                <p className="text-xs text-slate-500 font-medium">Target: {selectedUser.name}</p>
                            </div>
                            <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600 transition-colors">
                                <ArrowDownRight className="rotate-[-45deg]" size={24} />
                            </button>
                        </div>

                        <div className="p-6 space-y-6">
                            {/* Trading Mode Toggle */}
                            <div className="space-y-3">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Execution Mode</label>
                                <div className="flex p-1 bg-slate-100 rounded-xl">
                                    <button
                                        onClick={() => setTradingMode('AUTO')}
                                        className={`flex-1 py-2 text-xs font-black rounded-lg transition-all ${tradingMode === 'AUTO' ? 'bg-white shadow-sm text-primary' : 'text-slate-500 hover:text-slate-800'}`}
                                    >
                                        Auto-Pilot
                                    </button>
                                    <button
                                        onClick={() => setTradingMode('MANUAL')}
                                        className={`flex-1 py-2 text-xs font-black rounded-lg transition-all ${tradingMode === 'MANUAL' ? 'bg-white shadow-sm text-orange-600' : 'text-slate-500 hover:text-slate-800'}`}
                                    >
                                        Manual Override
                                    </button>
                                </div>
                                <p className="text-[10px] text-slate-400 leading-relaxed px-1">
                                    {tradingMode === 'AUTO'
                                        ? "User portfolio is fully managed by AI algorithms based on risk tolerance."
                                        : "User has full discretion to execute trades. AI only provides signals."}
                                </p>
                            </div>

                            {/* Industry Restrictions */}
                            <div className="space-y-3">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Authorized Industries</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {SECTORS.map(sector => (
                                        <button
                                            key={sector}
                                            onClick={() => toggleSector(sector)}
                                            className={`px-3 py-2 rounded-lg text-xs font-bold text-left transition-all border ${allowedSectors.includes(sector)
                                                ? 'bg-indigo-50 border-indigo-200 text-indigo-700'
                                                : 'bg-white border-slate-100 text-slate-400 hover:border-slate-300'
                                                }`}
                                        >
                                            <div className="flex items-center justify-between">
                                                {sector}
                                                {allowedSectors.includes(sector) && <Shield size={12} />}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Audit Log Input */}
                            <div className="space-y-3">
                                <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Action Comments (Audit Log)</label>
                                <textarea
                                    value={adminComment}
                                    onChange={(e) => setAdminComment(e.target.value)}
                                    placeholder="e.g. User requested manual control via email on Feb 1st..."
                                    className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary/20 min-h-[80px] font-medium text-slate-700"
                                />
                            </div>

                            <button
                                data-testid="confirm-policy-button"
                                onClick={handleSaveConfig}
                                disabled={!adminComment}
                                className="w-full py-4 bg-[#0A2A4D] disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#0A2A4D]/90 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-900/20"
                            >
                                <Shield size={16} />
                                Confirm Policy Update
                            </button>
                        </div>
                    </Card>
                </div>
            )}
        </div>
    );
}
