import React, { useState, useEffect } from 'react';
import { Card } from "./ui/card";
import { socket } from "../services/api";
import { History, Brain } from "lucide-react";

export function AIAnalyst() {
    const [prediction, setPrediction] = useState("Analyzing real-time market microstructure...");
    const [history, setHistory] = useState([]);
    const [view, setView] = useState("CURRENT"); // CURRENT | HISTORY

    useEffect(() => {
        socket.on('steward_prediction', (data) => {
            if (data.prediction) setPrediction(data.prediction);
            if (data.history) setHistory(data.history);
        });

        return () => {
            socket.off('steward_prediction');
        };
    }, []);

    return (
        <Card className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white border-none shadow-xl overflow-hidden relative flex flex-col h-full">
            <div className="p-6 relative z-10 flex-1 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <div className="px-2 py-0.5 rounded bg-green-500 text-[10px] font-bold uppercase tracking-wider">Groq Llama-3 Powered</div>
                        <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                    </div>
                    <button
                        onClick={() => setView(view === 'CURRENT' ? 'HISTORY' : 'CURRENT')}
                        className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-indigo-200 hover:text-white"
                        title="Toggle History"
                    >
                        {view === 'CURRENT' ? <History size={16} /> : <Brain size={16} />}
                    </button>
                </div>

                <h3 className="text-xl font-bold mb-2">Portfolio Intelligence</h3>

                {view === 'CURRENT' ? (
                    <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                        <p className="text-sm text-slate-300 mb-6 leading-relaxed min-h-[80px]">
                            {prediction}
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
                    </div>
                ) : (
                    <div className="animate-in fade-in slide-in-from-left-4 duration-300 flex-1 overflow-y-auto pr-2 max-h-[200px] scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
                        <div className="space-y-3">
                            {history.length === 0 ? (
                                <p className="text-xs text-slate-500 italic">No history logged yet.</p>
                            ) : history.map((item, i) => (
                                <div key={i} className="pb-3 border-b border-white/5 last:border-0">
                                    <p className="text-[10px] text-indigo-300 font-bold mb-0.5">{item.time}</p>
                                    <p className="text-xs text-slate-300 leading-relaxed">{item.text}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Background decoration */}
            <div className="absolute -right-10 -top-10 h-40 w-40 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -left-10 -bottom-10 h-40 w-40 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />
        </Card>
    );
}
