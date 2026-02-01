import React from 'react';
import { Card } from "../components/ui/card";
import { useUser } from "../context/UserContext";
import { HelpCircle, Shield, Zap, FileText, Briefcase, CheckCircle2 } from 'lucide-react';

const HELP_DATA = {
    ADMIN: {
        title: "Superadmin Command Manual",
        icon: Shield,
        color: "text-indigo-600",
        bgColor: "bg-indigo-50",
        sections: [
            { title: "System Oversight", items: ["Global Strategy Monitoring", "Node Telemetry", "Audit Logs"] },
            { title: "User & Access Management", items: ["Role Assignment", "Session Security", "Credential Rotation"] },
            { title: "Infrastructure Config", items: ["API Gateways", "Model Tuning"] }
        ]
    },
    USER: {
        title: "Trader / Investor Manual",
        icon: Zap,
        color: "text-primary",
        bgColor: "bg-primary/5",
        sections: [
            { title: "Portfolio Management", items: ["Real-time Metrics", "Exposure Control", "Equity Curve"] },
            { title: "Trading Hub", items: ["Autonomous Execution", "Strategic Overlap", "Manual Overrides"] },
            { title: "Reports & Analytics", items: ["Performance Summaries", "Tax Harvesting"] }
        ]
    },
    AUDITOR: {
        title: "Auditor / Compliance Manual",
        icon: FileText,
        color: "text-amber-600",
        bgColor: "bg-amber-50",
        sections: [
            { title: "Audit Integrity", items: ["Global Audit Trail", "Decision Logic", "Cryptographic Verification"] },
            { title: "Reporting", items: ["Risk Exposure Reports", "Regulatory Exports"] },
            { title: "Restrictions", items: ["Read-Only Access Verification"] }
        ]
    },
    BUSINESS_OWNER: {
        title: "Executive Manual",
        icon: Briefcase,
        color: "text-purple-600",
        bgColor: "bg-purple-50",
        sections: [
            { title: "High-Level Metrics", items: ["Total Managed Assets (TMA)", "Portfolio ROI", "Revenue Monitoring"] },
            { title: "Strategic Insights", items: ["Agent Intelligence Summaries", "Market Movers Monitoring"] },
            { title: "Subscription Management", items: ["Enterprise SLAs", "White-label Options"] }
        ]
    }
};

export function Help() {
    const { user } = useUser();
    const role = user?.role || 'USER';
    const data = HELP_DATA[role] || HELP_DATA.USER;
    const Icon = data.icon;

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500 pb-20">
            <header className="flex items-center gap-6 p-8 rounded-3xl bg-slate-900 text-white overflow-hidden relative shadow-2xl">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-[80px]" />
                <div className={`p-4 rounded-2xl ${data.bgColor} ${data.color} shadow-lg shadow-black/20`}>
                    <Icon size={32} />
                </div>
                <div>
                    <h1 className="text-3xl font-black tracking-tight font-heading">{data.title}</h1>
                    <p className="text-slate-400 mt-1 font-medium italic">Authorized Documentation for {role} role.</p>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {data.sections.map((section, idx) => (
                    <Card key={idx} className="p-8 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                        <h3 className="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                            <HelpCircle size={18} className="text-primary" />
                            {section.title}
                        </h3>
                        <ul className="space-y-4">
                            {section.items.map((item, i) => (
                                <li key={i} className="flex items-start gap-3 group">
                                    <div className="mt-1">
                                        <CheckCircle2 size={14} className="text-green-500 group-hover:scale-110 transition-transform" />
                                    </div>
                                    <span className="text-sm font-semibold text-slate-600 group-hover:text-slate-900 transition-colors">{item}</span>
                                </li>
                            ))}
                        </ul>
                    </Card>
                ))}

                <Card className="p-8 border-primary/20 bg-primary/5 shadow-sm md:col-span-2">
                    <div className="flex items-center gap-4">
                        <div className="h-10 w-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg">
                            <HelpCircle size={20} />
                        </div>
                        <div>
                            <h4 className="font-black text-slate-900">Need Advanced Assistance?</h4>
                            <p className="text-sm text-slate-500 mt-1">Our technical support team is available 24/7 for Enterprise SLA clients.</p>
                        </div>
                        <button className="ml-auto px-6 py-2.5 bg-slate-900 text-white text-xs font-black rounded-lg uppercase tracking-widest hover:bg-slate-800 transition-all">
                            Open Ticket
                        </button>
                    </div>
                </Card>
            </div>

            <footer className="text-center text-slate-400">
                <p className="text-[10px] font-black uppercase tracking-[0.3em]">StockSteward AI • Confidential Documentation • v4.0.2</p>
            </footer>
        </div>
    );
}
