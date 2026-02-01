import React from 'react';
import { Card } from "./ui/card";

export function AIAnalyst() {
    return (
        <Card className="p-6 bg-gradient-to-br from-indigo-900 to-slate-900 text-white border-none shadow-xl overflow-hidden relative">
            <div className="relative z-10">
                <div className="flex items-center gap-2 mb-4">
                    <div className="px-2 py-0.5 rounded bg-green-500 text-[10px] font-bold uppercase tracking-wider">Groq Llama-3 Powered</div>
                    <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                </div>

                <h3 className="text-xl font-bold mb-2">Portfolio Intelligence</h3>
                <p className="text-sm text-slate-300 mb-6 leading-relaxed">
                    Based on current market volatility and your risk profile, I recommend increasing exposure to **Energy** sectors.
                    Sentiment analysis shows a "Bullish" trend in traditional energy over the next 15 days.
                </p>

                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/5 rounded-xl p-3 backdrop-blur-sm border border-white/10">
                        <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">Steward Conviction</div>
                        <div className="text-lg font-bold text-green-400">92%</div>
                    </div>
                    <div className="bg-white/5 rounded-xl p-3 backdrop-blur-sm border border-white/10">
                        <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">Expected Alpha</div>
                        <div className="text-lg font-bold">+4.5%</div>
                    </div>
                </div>

                <button className="w-full mt-6 py-3 rounded-xl bg-white text-indigo-900 font-bold text-sm transition-transform hover:scale-[1.02] active:scale-[0.98]">
                    Review Trade Proposal
                </button>
            </div>

            {/* Background decoration */}
            <div className="absolute -right-10 -top-10 h-40 w-40 bg-indigo-500/20 rounded-full blur-3xl" />
            <div className="absolute -left-10 -bottom-10 h-40 w-40 bg-purple-500/20 rounded-full blur-3xl" />
        </Card>
    );
}
