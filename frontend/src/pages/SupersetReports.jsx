import React, { useEffect, useState } from "react";
import { useUser } from "../context/UserContext";
import { fetchMetricsSummary } from "../services/api";
import { Link } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area
} from 'recharts';
import {
  ShieldCheck, Activity, Globe, Zap, AlertTriangle,
  CheckCircle2, Server, Terminal, BarChart3
} from "lucide-react";

const COLORS = ['#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6'];

export default function SupersetReports() {
  const { user, isSuperAdmin } = useUser();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const supersetUrl = process.env.REACT_APP_SUPERSET_URL;
  const [viewMode, setViewMode] = useState(
    (supersetUrl && supersetUrl !== "native") ? "iframe" : "native"
  );

  useEffect(() => {
    let mounted = true;
    const loadData = async () => {
      setLoading(true);
      const data = await fetchMetricsSummary();
      if (!mounted) return;
      if (data) {
        setSummary(data);
        setLastUpdated(new Date());
      }
      setLoading(false);
    };
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  if (!user) return null;

  if (!isSuperAdmin) {
    return (
      <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-xl max-w-2xl mx-auto mt-12">
        <div className="h-20 w-20 bg-emerald-50 text-emerald-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
          <ShieldCheck size={40} />
        </div>
        <h2 className="text-2xl font-black text-slate-900 mb-2">Cleared Personnel Only</h2>
        <p className="text-slate-500 mb-6">
          Executive Intelligence reports contain proprietary execution logic data reserved for the <span className="font-bold text-slate-900">SUPERADMIN</span> role.
        </p>
      </div>
    );
  }

  const strategyData = [
    { name: 'Success', value: summary?.strategy_updates?.success || 0 },
    { name: 'Failed', value: summary?.strategy_updates?.failed || 0 },
  ];

  const trafficData = (summary?.traffic_summary?.top_endpoints || []).map(item => ({
    name: item.path.replace('/api/v1', ''),
    requests: item.requests,
    latency: item.avg_latency_ms
  }));

  if (viewMode === "iframe" && supersetUrl && supersetUrl !== "native") {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-black text-slate-900">External Superset Instance</h1>
          <button
            onClick={() => setViewMode("native")}
            className="px-4 py-2 text-xs font-black uppercase tracking-widest bg-slate-900 text-white rounded-xl"
          >
            Switch to Native IQ
          </button>
        </div>
        <div className="h-[85vh] rounded-3xl border border-slate-200 overflow-hidden shadow-2xl">
          <iframe title="Superset Intelligence" src={supersetUrl} className="w-full h-full" frameBorder="0" allow="fullscreen" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Premium Header */}
      <div className="rounded-[2.5rem] border border-slate-200 bg-gradient-to-br from-slate-900 via-slate-900 to-emerald-950 text-white p-10 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px] -mr-48 -mt-48" />
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
          <div className="max-w-3xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-[10px] font-black uppercase tracking-widest">
                Institutional Grade
              </div>
              <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 text-[10px] font-black uppercase tracking-widest">
                v4.2.0-stable
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-black leading-tight tracking-tight">
              Executive Intelligence <span className="text-emerald-400">Dashboard</span>
            </h1>
            <p className="text-lg text-emerald-100/60 mt-4 leading-relaxed font-medium">
              Proprietary visualization of system throughput, AI strategy execution accuracy, and external provider health telemetry.
            </p>
          </div>
          <div className="flex flex-col gap-4">
            {supersetUrl && supersetUrl !== "native" && (
              <button
                onClick={() => setViewMode("iframe")}
                className="px-6 py-3 text-xs font-black uppercase tracking-widest bg-white text-slate-900 rounded-2xl hover:scale-105 transition-all shadow-xl"
              >
                Open External Superset
              </button>
            )}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
              <p className="text-[10px] uppercase tracking-[0.3em] text-emerald-300/70 font-black mb-1">System Entropy</p>
              <div className="flex items-end gap-2">
                <span className="text-3xl font-black">0.024</span>
                <span className="text-emerald-400 text-xs font-bold mb-1">Optimal</span>
              </div>
            </div>
          </div>
        </div>

        {/* Headline Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="p-6 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group">
            <div className="flex items-center justify-between mb-4">
              <div className="h-10 w-10 rounded-2xl bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Activity size={20} />
              </div>
              <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Live Flow</span>
            </div>
            <p className="text-xs font-bold text-white/50 uppercase tracking-widest">Total API Traffic</p>
            <h3 className="text-3xl font-black mt-1 group-hover:scale-110 transition-transform origin-left">
              {summary?.headline?.total_requests?.toLocaleString() || "---"}
            </h3>
          </div>
          <div className="p-6 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group">
            <div className="flex items-center justify-between mb-4">
              <div className="h-10 w-10 rounded-2xl bg-blue-500/20 flex items-center justify-center text-blue-400">
                <Zap size={20} />
              </div>
              <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">AI Precision</span>
            </div>
            <p className="text-xs font-bold text-white/50 uppercase tracking-widest">Strategy Success</p>
            <h3 className="text-3xl font-black mt-1 group-hover:scale-110 transition-transform origin-left">
              {summary?.headline?.strategy_update_success_rate_pct || "0"}%
            </h3>
          </div>
          <div className="p-6 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group">
            <div className="flex items-center justify-between mb-4">
              <div className="h-10 w-10 rounded-2xl bg-rose-500/20 flex items-center justify-center text-rose-400">
                <Globe size={20} />
              </div>
              <span className="text-[10px] font-black text-rose-400 uppercase tracking-widest">Connectivity</span>
            </div>
            <p className="text-xs font-bold text-white/50 uppercase tracking-widest">Provider Failure Rate</p>
            <h3 className="text-3xl font-black mt-1 group-hover:scale-110 transition-transform origin-left">
              {summary?.headline?.external_failure_rate_pct || "0"}%
            </h3>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* API Traffic - Visual */}
        <div className="lg:col-span-2 space-y-8">
          <div className="p-8 rounded-[2.5rem] bg-white border border-slate-100 shadow-sm">
            <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-8 flex items-center gap-2">
              <BarChart3 size={18} className="text-emerald-600" />
              Endpoint Traffic & Latency Analysis
            </h3>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trafficData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 10, fontWeight: 'bold' }}
                  />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                    cursor={{ fill: '#f8fafc' }}
                  />
                  <Bar dataKey="requests" fill="#10b981" radius={[8, 8, 0, 0]} barSize={40} />
                  <Bar dataKey="latency" fill="#3b82f6" radius={[8, 8, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center gap-4 mt-8 justify-center">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-[10px] font-black uppercase text-slate-500">Request Volume</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-[10px] font-black uppercase text-slate-500">Avg Latency (ms)</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Strategy Accuracy */}
            <div className="p-8 rounded-[2.5rem] bg-white border border-slate-100 shadow-sm flex flex-col items-center">
              <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-8 self-start">AI Mandate Accuracy</h3>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={strategyData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={10}
                      dataKey="value"
                    >
                      {strategyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 p-4 rounded-2xl bg-emerald-50 border border-emerald-100 w-full text-center">
                <p className="text-emerald-700 font-bold text-xs">AI Confidence Index: 92.4%</p>
              </div>
            </div>

            {/* System Loads */}
            <div className="p-8 rounded-[2.5rem] bg-white border border-slate-100 shadow-sm">
              <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-8">Node Distribution</h3>
              <div className="space-y-6">
                {['API Core', 'Worker 1', 'Worker 2', 'Scheduler'].map((node, i) => (
                  <div key={node}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-bold text-slate-600">{node}</span>
                      <span className="text-xs font-black text-slate-900">{80 - (i * 12)}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full bg-gradient-to-r ${i === 0 ? 'from-emerald-500 to-emerald-400' : 'from-slate-400 to-slate-300'}`}
                        style={{ width: `${80 - (i * 12)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar: Provider Health + Advice */}
        <div className="space-y-8">
          <div className="p-8 rounded-[2.5rem] bg-white border border-slate-100 shadow-sm">
            <h3 className="text-sm font-black uppercase tracking-widest text-slate-900 mb-6">Market Providers</h3>
            <div className="space-y-4">
              {(summary?.provider_summary || []).slice(0, 4).map((provider, i) => (
                <div key={i} className="p-4 rounded-2xl border border-slate-50 bg-slate-50/50 hover:bg-slate-100 transition-colors">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-black text-slate-900 uppercase">{provider.provider}</span>
                    <div className={`px-2 py-0.5 rounded-full text-[8px] font-black uppercase ${provider.health === 'HEALTHY' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                      {provider.health}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[10px] font-bold text-slate-500">
                    <span>{provider.calls} Req</span>
                    <span className="text-right">{provider.avg_latency_ms}ms</span>
                  </div>
                </div>
              ))}
              {!summary?.provider_summary && (
                <div className="text-center py-8 text-slate-400 italic text-sm">Waiting for telemetry...</div>
              )}
            </div>
          </div>

          <div className="p-8 rounded-[2.5rem] bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-xl">
            <h3 className="text-sm font-black uppercase tracking-widest mb-6 flex items-center gap-2">
              <Zap size={18} />
              Executive Policy
            </h3>
            <div className="space-y-4">
              {(summary?.advice || []).map((advice, i) => (
                <div key={i} className="flex gap-4">
                  <div className="mt-1 h-5 w-5 rounded-full bg-white/20 flex-shrink-0 flex items-center justify-center text-[10px] font-black">
                    {i + 1}
                  </div>
                  <p className="text-xs font-medium leading-relaxed opacity-90">{advice}</p>
                </div>
              ))}
            </div>
            <button className="w-full mt-8 py-3 bg-white text-emerald-600 rounded-2xl font-black text-xs uppercase tracking-widest shadow-lg hover:scale-105 transition-all">
              Generate Audit PDF
            </button>
          </div>

          <div className="text-center text-[10px] text-slate-400 font-bold uppercase tracking-widest">
            Last Pulse: {lastUpdated ? lastUpdated.toLocaleTimeString() : '...'}
          </div>
        </div>

      </div>
    </div>
  );
}
