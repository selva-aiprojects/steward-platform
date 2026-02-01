import React, { useEffect, useState } from 'react';
import { Card } from "../components/ui/card";
import { User, Wallet, Shield, PieChart, ArrowUpRight, ArrowDownRight } from "lucide-react";

export function Users() {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        const mockUsers = [
            { id: 1, name: "Alexander Pierce", email: "alex@stocksteward.ai", status: "ACTIVE", used: 125000, unused: 45000, risk: "MODERATE", win_rate: "68%" },
            { id: 2, name: "Sarah Connor", email: "sarah.c@sky.net", status: "ACTIVE", used: 250000, unused: 12000, risk: "HIGH", win_rate: "74%" },
            { id: 3, name: "Tony Stark", email: "tony@starkintl.ai", status: "ACTIVE", used: 840000, unused: 50000, risk: "AGGRESSIVE", win_rate: "81%" },
            { id: 4, name: "Bruce Wayne", email: "bruce@waynecorp.com", status: "IDLE", used: 0, unused: 1000000, risk: "LOW", win_rate: "0%" },
            { id: 5, name: "Natasha Romanoff", email: "nat@shield.gov", status: "ACTIVE", used: 95000, unused: 5000, risk: "MODERATE", win_rate: "62%" },
        ];
        setUsers(mockUsers);
    }, []);

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
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
                                <div className="mt-4 flex items-center gap-2">
                                    <span className={`px-2 py-0.5 rounded text-[8px] font-black tracking-widest uppercase ${user.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-400'
                                        }`}>{user.status}</span>
                                    <span className="text-[10px] text-slate-500 font-bold">Risk: {user.risk}</span>
                                </div>
                            </div>

                            {/* Fund Report */}
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
        </div>
    );
}
